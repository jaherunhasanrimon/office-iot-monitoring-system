// GPIO Mapping
#define LIGHT1 18
#define LIGHT2 21
#define LIGHT3 22
#define FAN1   19
#define FAN2   23

void setup() {

  pinMode(LIGHT1, OUTPUT);
  pinMode(LIGHT2, OUTPUT);
  pinMode(LIGHT3, OUTPUT);
  pinMode(FAN1, OUTPUT);
  pinMode(FAN2, OUTPUT);

  // সব OFF
  digitalWrite(LIGHT1, HIGH);
  digitalWrite(LIGHT2, HIGH);
  digitalWrite(LIGHT3, HIGH);
  digitalWrite(FAN1, HIGH);
  digitalWrite(FAN2, HIGH);
}

void loop() {

  // সব ON
  digitalWrite(LIGHT1, LOW);
  digitalWrite(LIGHT2, LOW);
  digitalWrite(LIGHT3, LOW);
  digitalWrite(FAN1, LOW);
  digitalWrite(FAN2, LOW);

  delay(3000);

  // সব OFF
  digitalWrite(LIGHT1, HIGH);
  digitalWrite(LIGHT2, HIGH);
  digitalWrite(LIGHT3, HIGH);
  digitalWrite(FAN1, HIGH);
  digitalWrite(FAN2, HIGH);

  delay(3000);
}