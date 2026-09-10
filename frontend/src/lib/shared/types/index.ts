export type JsonObject = { [key: string]: JsonValue };

export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | JsonObject;

export type AppNavItem = {
  href: "/" | "/goals" | "/settings";
  label: string;
};
