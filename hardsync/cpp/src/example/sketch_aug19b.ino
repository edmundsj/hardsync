#include "parser.h"
#include "comms.h"


class CommunicationClient : public BaseCommunicationClient {
public:
    double measureVoltage() const override {
        return 3.3;
    }
    String identify() const override {
      return "FQNONEUT";
    }
};

CommunicationClient client = CommunicationClient();

void setup() {
  client.begin();
  
  String line = "MeasureVoltageRequest(channel=1,integration_time=0.5)";
  ParsedFunction pf = parseFunction(line);
  String args = extractArgs(line);
  
  Serial.println("Function name: " + pf.name);
  Serial.println("Function arguments: " + args);
  for (int i = 0; i < pf.argCount; i++) {
    Serial.println("Argument: " + pf.arguments[i].key + ", Value: " + pf.arguments[i].value);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  client.checkMessage();
}
