#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <MPU6050.h>
#include <math.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT22.h>

const char* ssid = "NUME_HOTSPOT";
const char* password = "PAROLA";
const char* mqtt_server = "IP";

Adafruit_BMP280 bmp;
MPU6050 mpu;
const int dhtPin = 15;
float sensorVal = 0;
const int anPin= 0;
WiFiClient espClient;
PubSubClient client(espClient);
DHT22 dhtsens(dhtPin);
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

  //WiFi
  setup_wifi();
  client.setServer(mqtt_server, 1883);

  //BMP280
  if (!bmp.begin(0x76)) {
    Serial.println("Error BMP280");
    while (1);
  } else {
    Serial.println("BMP280 OK");
  }

  //MPU6050
  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("Error MPU6050");
    while (1);
  } else {
    Serial.println("MPU6050 OK");
  }
}

void loop() {
  sensorVal = analogRead(anPin);
  //WiFi
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  //BMP280
  float temp = bmp.readTemperature();
  float pres = bmp.readPressure()/100;
  float alt = bmp.readAltitude(1013.0);

  //MPU6050
  int16_t ax, ay, az, gx, gy, gz;
  mpu.getAcceleration(&ax, &ay, &az); 
  mpu.getRotation(&gx, &gy, &gz);
  float gx_u = gx / 131.0;
  float gy_u = gy / 131.0;
  float gz_u = gz / 131.0;
  float ax_u = ax / 16384.0;
  float ay_u = ay / 16384.0;
  float az_u = az / 16384.0;

  float roll  = atan2(ay_u, az_u) * 180 / PI;
  float pitch = atan2(-ax_u, sqrt(ay_u * ay_u + az_u * az_u)) * 180 / PI;
  static unsigned long lastDHTRead = 0;
  static float humid = 0;
  static float tempDHT = 0;

  if (millis() - lastDHTRead > 2000) {
  humid = dhtsens.getHumidity();
  tempDHT = dhtsens.getTemperature();
  lastDHTRead = millis();
  }
  static unsigned long lastMsg = 0;
  if(millis() - lastMsg > 100)
  {
    lastMsg = millis();

    char msg[200];
    sprintf(msg, "Xaccel: %.2f Yaccel: %.2f Zaccel: %.2f Xgyro:%.2f Ygyro:%.2f Zgyro:%.2f Roll:%.2f Pitch:%.2f Presiune:%.2f TemperChip:%.2f Altitudine:%2f TempOut:%.2f Umid:%.2f Gaz:%.2f", 
        ax_u, ay_u, az_u, gx_u, gy_u, gz_u, roll, pitch, pres, temp, alt, tempDHT, humid, sensorVal);
    Serial.println(msg);
    client.publish("esp32", msg);
  }
}