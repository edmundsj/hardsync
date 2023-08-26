#include "client.h"
#include "parser.h"

class MyClient : public Client {
    // {{core_implementations}}
};
MyClient client = MyClient();

void setup() {
    client.begin();
}
void loop() {
    client.respond();
}