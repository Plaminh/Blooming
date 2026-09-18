export type CompanionWidgetKind =
  "focusing" | "ending" | "paused" | "behindSchedule" | "offline" | "reminders";

export type PlantSpecies =
  "monstera" | "sunflower" | "bonsai" | "jasmine" | "lavender";

export type PlantFrameIndex =
  0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15;

export interface ActivePlantPresentation {
  species: PlantSpecies;
  frameIndex: PlantFrameIndex;
  scale?: number;
}

type WidgetScenePresentation = {
  /** Presentation-only lifecycle state; this feature performs no growth logic. */
  activePlant: ActivePlantPresentation | null;
};

export type ReminderItem = {
  id: string;
  /** Full accessible and visual source text. CSS may ellipsis; do not truncate this string. */
  label: string;
};

export type PausedPresentation = WidgetScenePresentation & {
  kind: "paused";
  speechText: string;
  timeText?: string;
  onResume?: () => void;
  onEnd?: () => void;
};

export type BehindSchedulePresentation = WidgetScenePresentation & {
  kind: "behindSchedule";
  speechText: string;
  onReplan?: () => void;
  onLater?: () => void;
  onOpen?: () => void;
};

export type OfflinePresentation = WidgetScenePresentation & {
  kind: "offline";
  speechText: string;
  timeText?: string;
};

export type RemindersPresentation = WidgetScenePresentation & {
  kind: "reminders";
  reminders: ReminderItem[];
  onView?: () => void;
  onDismiss?: () => void;
};

export type FocusingPresentation = WidgetScenePresentation & {
  kind: "focusing";
  timeText: string;
  onPause?: () => void;
  onEnd?: () => void;
};

export type EndingPresentation = WidgetScenePresentation & {
  kind: "ending";
  speechText: string;
  timeText?: string;
  onDone?: () => void;
  onFinishedEarly?: () => void;
  onNeedMoreTime?: () => void;
  onSkip?: () => void;
};

export type CompanionWidgetPresentation =
  | FocusingPresentation
  | EndingPresentation
  | PausedPresentation
  | BehindSchedulePresentation
  | OfflinePresentation
  | RemindersPresentation;

export type CompanionWidgetProps = {
  presentation: CompanionWidgetPresentation;
  weather?: import("../model/environment").Weather;
  timezone?: string;
  rainEnabled?: boolean;
};

export type WidgetActionVariant = "primary" | "secondary";

export type WidgetActionIcon = "play" | "stop";

export type WidgetAction = {
  id: string;
  label: string;
  variant: WidgetActionVariant;
  icon?: WidgetActionIcon;
  onClick?: () => void;
};
