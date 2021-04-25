#include <LiquidCrystal.h>

// pin settings for the lcd
LiquidCrystal lcd = LiquidCrystal(2, 3, 4, 5, 6, 7);

// number of milliseconds to wait between detecting a serial message and processing it
int messageProcessDelay = 100;

// input arriving at the serial port is stored here
String serialInput;

// the two lines currently displayed on the display
String displayLines [2];

void setup() {
    // set up the LCD's number of columns and rows:
    lcd.begin(16, 2);

    // initialize the serial communications:
    Serial.begin(9600);
}

void loop() {
    // when characters arrive over the serial port...
    if (Serial.available()) {
        // wait a bit for the entire message to arrive
        delay(messageProcessDelay);
        // read all the available characters into a string
        serialInput= Serial.readString();

        // split the input string into 16-char substrings and save into displayLines
        if (serialInput.length() <= 16) {
            displayLines[0] = serialInput;
            displayLines[1] = "";
        } else if (serialInput.length() <= 32) {
            displayLines[0] = serialInput.substring(0, 16);
            displayLines[1] = serialInput.substring(16, serialInput.length());
        } else {
            // truncate input strings larger than 32 chars
            displayLines[0] = serialInput.substring(0, 16);
            displayLines[1] = serialInput.substring(16, 32);
        }

        // clear screen and print first line on first row
        lcd.clear();
        lcd.print(displayLines[0]);
        // print second line on second row
        lcd.setCursor(0, 1);
        lcd.print(displayLines[1]);
    }
}
