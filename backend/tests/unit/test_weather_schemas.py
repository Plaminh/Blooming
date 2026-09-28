from app.schemas.weather import PlaceCandidate


def test_place_candidate_rounds_coordinates():
    candidate = PlaceCandidate(name="London", lat=51.5074, lon=-0.1278)
    assert candidate.lat == 51.51
    assert candidate.lon == -0.13

    candidate2 = PlaceCandidate(name="Somewhere", lat=10.1, lon=20.0)
    assert candidate2.lat == 10.1
    assert candidate2.lon == 20.0
