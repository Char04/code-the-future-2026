#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

const char* ssid = "NAME";
const char* password = "PASSWORD";

const char* mqtt_server = "IP"; 

#define SDA_PIN 6
#define SCL_PIN 7

WiFiClient espClient;
PubSubClient client(espClient);
Adafruit_MPU6050 mpu;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to: ");
  Serial.println(ssid);

  WiFi.setSleep(false);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
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
  delay(3000); 

  setup_wifi();
  client.setServer(mqtt_server, 1883);

  Wire.begin(SDA_PIN, SCL_PIN);
  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("MPU6050 not found");
    while (1) { delay(10); } 
  }
  Serial.println("MPU6050 initialized");
  
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  static unsigned long lastMsg = 0;
  if (millis() - lastMsg > 500) {
    lastMsg = millis();

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    char msg[50];
    sprintf(msg, "X:%.2f Y:%.2f Z:%.2f", g.gyro.x, g.gyro.y, g.gyro.z);

    Serial.print("Publishing: ");
    Serial.println(msg);

    client.publish("esp32/giroscop", msg);
  }
}