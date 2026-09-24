import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from app.db.models.users import UserSettings

@pytest.mark.asyncio
async def test_bootstrap_weather_schema_matches_orm(db_session):
    columns = (
        await db_session.execute(
            text("""
        SELECT column_name, data_type, numeric_precision, numeric_scale, column_default
        FROM information_schema.columns
        WHERE table_name = 'user_settings'
    """)
        )
    ).all()
    actual = {row.column_name: row for row in columns}
    for name in (
        "weather_location",
        "weather_location_name",
        "weather_lat",
        "weather_lon",
        "scene_season",
    ):
        assert name in actual
        assert name in UserSettings.__table__.columns
    for name, precision in [("weather_lat", 5), ("weather_lon", 6)]:
        assert actual[name].data_type == "numeric"
        assert actual[name].numeric_precision == precision
        assert actual[name].numeric_scale == 2
        assert UserSettings.__table__.columns[name].type.precision == precision
        assert UserSettings.__table__.columns[name].type.scale == 2
        
    assert actual["scene_season"].column_default == "'AUTO'::character varying"

    constraints = (
        (
            await db_session.execute(
                text("""
        SELECT conname FROM pg_constraint WHERE conrelid = 'user_settings'::regclass
    """)
            )
        )
        .scalars()
        .all()
    )
    expected = {
        constraint.name
        for constraint in UserSettings.__table__.constraints
        if constraint.name
    }
    assert expected <= set(constraints)

@pytest.mark.asyncio
async def test_weather_schema_constraint_behavior(db_session):
    # Setup test user
    uid = (await db_session.execute(text("INSERT INTO users(email, password_hash) VALUES ('weather-schema@test.local', 'test') RETURNING id"))).scalar()
    await db_session.commit()
    
    try:
        # Accepts: legacy free text, both coordinates null
        await db_session.execute(text("INSERT INTO user_settings(user_id, weather_location) VALUES (:uid, 'Legacy free text')"), {"uid": uid})
        await db_session.commit()

        # Check default season
        season = (await db_session.execute(text("SELECT scene_season FROM user_settings WHERE user_id = :uid"), {"uid": uid})).scalar()
        assert season == 'AUTO'
        
        # Accepts: valid approximate coordinates with rounding
        await db_session.execute(text("UPDATE user_settings SET weather_location_name = 'London', weather_lat = 51.5074, weather_lon = -0.1278 WHERE user_id = :uid"), {"uid": uid})
        await db_session.commit()
        
        row = (await db_session.execute(text("SELECT weather_lat, weather_lon FROM user_settings WHERE user_id = :uid"), {"uid": uid})).first()
        assert row.weather_lat == Decimal("51.51")
        assert row.weather_lon == Decimal("-0.13")

        # Invalid constraints testing
        invalid_updates = [
            # Latitude > 90
            "UPDATE user_settings SET weather_lat = 91 WHERE user_id = :uid",
            # Latitude < -90
            "UPDATE user_settings SET weather_lat = -91 WHERE user_id = :uid",
            # Longitude > 180
            "UPDATE user_settings SET weather_lon = 181 WHERE user_id = :uid",
            # Longitude < -180
            "UPDATE user_settings SET weather_lon = -181 WHERE user_id = :uid",
            # Invalid scene_season
            "UPDATE user_settings SET scene_season = 'MONSOON' WHERE user_id = :uid",
            # Latitude without longitude
            "UPDATE user_settings SET weather_lon = NULL WHERE user_id = :uid",
            # Longitude without latitude
            "UPDATE user_settings SET weather_lon = 0, weather_lat = NULL WHERE user_id = :uid",
            # Coordinates without weather_location_name
            "UPDATE user_settings SET weather_location_name = NULL WHERE user_id = :uid",
            # Blank or whitespace-only weather_location_name when coordinates exist
            "UPDATE user_settings SET weather_location_name = '   ' WHERE user_id = :uid",
        ]
        
        for statement in invalid_updates:
            with pytest.raises(IntegrityError):
                await db_session.execute(text(statement), {"uid": uid})
                await db_session.commit()
            await db_session.rollback()

    finally:
        await db_session.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": uid})
        await db_session.commit()
