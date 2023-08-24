#include "client.h"


class MyClient : public Client {
    // {{ user_implementations }}
};

MyClient client = MyClient();

void setup() {
    client.begin();
}

void loop() {
    client.respond();
}
