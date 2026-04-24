#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <MPU6050.h>
#include <math.h>
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "NUME_HOTSPOT";
const char* password = "PAROLA";
const char* mqtt_server = "IP";

Adafruit_BMP280 bmp;
MPU6050 mpu;
int sensorVal = 0;

WiFiClient espClient;
PubSubClient client(espClient);
void setup_wifi()
{
  delay(10);
  Serial.println();
  Serial.print("Connecting to: ");
  Serial.println(ssid);

  WiFi.setSleep(false);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}
void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT broker... ");
    String clientId = "ESP32_Gyro_Client_";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println("Connected");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}
void setup() {
  Serial.begin(115200);
  Wire.begin(6, 7);
  Serial.println("Pornire...");
  //WiFi
  setup_wifi();
  client.setServer(mqtt_server, 1883);

  // BMP280
  if (!bmp.begin(0x76)) {
    Serial.println("Eroare BMP280!");
    while (1);
  } else {
    Serial.println("BMP280 OK");
  }

  // MPU6050 
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("Eroare MPU6050!");
    while (1);
  } else {
    Serial.println("MPU6050 OK");
  }
}

void loop() {
  //WiFi
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  // BMP280 
  float temp = bmp.readTemperature();
  float pres = bmp.readPressure() / 100.0;

  // MPU6050 
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);

  float ax_g = ax / 16384.0;
  float ay_g = ay / 16384.0;
  float az_g = az / 16384.0;


  float roll  = atan2(ay_g, az_g) * 180 / PI;
  float pitch = atan2(-ax_g, sqrt(ay_g * ay_g + az_g * az_g)) * 180 / PI;

  static unsigned long lastMsg = 0;
  if(millis() - lastMsg > 500)
  {
    lastMsg = millis();

    char msg[150];
    sprintf(msg, "Xgyro:%.2f Ygyro:%.2f Zgyro:%.2f Roll:%.2f Pitch:%.2f Presiune:%.2f Temperatura:%2.f" , ax_g, ay_g, az_g, roll, pitch, pres, temp);
    Serial.print(msg);
    Serial.println(" ");
    client.publish("esp32", msg);
  }

  delay(500);
}