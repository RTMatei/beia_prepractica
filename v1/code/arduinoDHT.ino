#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  Serial.print("{\"temperature\": ");
  Serial.print(t);
  Serial.print(", \"humidity\": ");
  Serial.print(h);
  Serial.println("}");
  
  delay(5000);
}
