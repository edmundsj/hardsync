#include "client.h"

class MyClient : public Client {
    double measureVoltage(int channel, double integration_time) const {
        // YOUR measureVoltage CODE GOES HERE
    }
};

MyClient client = MyClient();

void setup() {
    client.begin();
}

void loop() {
    client.respond();
}
