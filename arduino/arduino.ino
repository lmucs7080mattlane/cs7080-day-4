#include <Firmata.h>
#include <pitches.h>

// The pin numbers for the digital pins on the arduino that we are using
// to control/read from:
// The LED
const int LED_PIN = 13;
// The Button
const int BUTTON_PIN = 9;
// The Buzzer
const int BUZZER_PIN = 8;

// Array of notes to play with the buzzer. The constants come
// from the 'pitches.h' file
const int TONE_LOOP_NUM_NOTES = 8;
const int TONE_LOOP_NOTES[TONE_LOOP_NUM_NOTES] = {
    NOTE_C5,
    NOTE_D5,
    NOTE_E5,
    NOTE_F5,
    NOTE_G5,
    NOTE_A5,
    NOTE_B5,
    NOTE_C6
};

// Firmata commands we can receive from the raspberry pi
// These need to be consistent with the ones in the
// raspberry pi code.
const byte FIRMATA_REQUEST_ALERT = 1;
const byte FIRMATA_REQUEST_BUTTON_STRING = 2;
const byte FIRMATA_REQUEST_BUTTON_INTEGER = 3;
// TODO challenge define a new command constant called
// 'FIRMATA_REQUEST_PLAY_NOTE' with value 4

// Firmata response commands we can send to the raspberry pi
// These need to be consistent with the ones in the
// raspberry pi code.
const byte FIRMATA_RESPONSE_BUTTON_STRING = 1;
const byte FIRMATA_RESPONSE_BUTTON_INTEGER = 2;

// When set to 1, sound the buzzer
int alert = 0;

// Initialise the firmata library so that we can talk to 
// the raspberry pi
void firmata_init(){
    // Register the function 'firmata_sysex_callback' with
    // the firmata library such that this function is called
    // whenever we receive a request from the raspberry pi
    Firmata.attach(START_SYSEX, firmata_sysex_callback);
    // Start listening for a raspberry pi connection
    Firmata.begin(57600);
}

// This function is here to make it easier to send 
// response strings back to the raspberry pi
void firmata_send_string(byte command, String message){
    // Send a message 'message' with command 'command'
    // to the raspberry pi
    String msg = String(char(command)) + message;
    int str_len = msg.length() + 1;
    char char_array[str_len];
    msg.toCharArray(char_array, str_len);
    Firmata.sendString(char_array);
}

// Turn LED light on
void turn_led_on(){
    digitalWrite(LED_PIN, HIGH);
}

// Turn LED light off
void turn_led_off(){
    digitalWrite(LED_PIN, LOW);
}

// Play a specific tone on the buzzer
// for a certain amount of milliseconds
void play_tone(int note, int milliseconds){
    tone(BUZZER_PIN, note, milliseconds);
}

// Function that when called repeatedly will
// play the notes in the TONE_LOOP_NOTES array
int current_beep_count = 0;
int current_beep_tone = 0;
void occasionally_beep(int beep_modulo, int beep_duration){
    if(current_beep_count++ % beep_modulo == 0){
        // Only play a tone once every 'beep_modulo' calls
        // to this function
        play_tone(TONE_LOOP_NOTES[current_beep_tone], beep_duration);
        // Move the beep tone to the next in the array
        // and loop back to the first note in the array
        // if we have reached the end
        current_beep_tone = ++current_beep_tone % TONE_LOOP_NUM_NOTES;
    }
    current_beep_count = current_beep_count % beep_modulo;
}

// This is the function that handles messages from the raspberry pi
// (through the 'firmata' library over the USB link)
void firmata_sysex_callback(byte command, byte argc, byte *argv)
{  
    // Perform different actions depending on which command
    // we received from the raspberry pi
    switch (command) {
        byte alert_parameter;
        case FIRMATA_REQUEST_ALERT:
            // We received an REQUEST_ALERT command
            // We know from the raspberry pi code that the
            // the alert command is sent with single parameter
            // which describes whether we the arduino should
            // be alerted or not. This parameter is one byte long.
            
            alert_parameter = argv[0]; // Get the first (and only)
            // byte from the data we received from the raspberry pi
            
            if (alert_parameter) {
                alert = 1;
                turn_led_on();
            }
            else {
                alert = 0;
                turn_led_off();
            }
            break;

        case FIRMATA_REQUEST_BUTTON_STRING:
            // We received a 'REQUEST_BUTTON_STRING' command.
            // This is a request from the raspberry pi
            // for the arduino to send a bit of text or
            // 'string' to the raspberry pi describing
            // the status of our button.
            if (digitalRead(BUTTON_PIN) == LOW) {
                firmata_send_string(
                    FIRMATA_RESPONSE_BUTTON_STRING,
                    String("Button is pressed")
                );
            }
            else {
                firmata_send_string(
                    FIRMATA_RESPONSE_BUTTON_STRING,
                    String("Button is not pressed")
                );
            }
            break;

        case FIRMATA_REQUEST_BUTTON_INTEGER:
            // We received a 'REQUEST_BUTTON_INTEGER' command.
            // This is a request from the raspberry pi
            // for the arduino to send an integer to the
            // raspberry pi describing the status of our button.
            firmata_send_string(
                FIRMATA_RESPONSE_BUTTON_INTEGER,
                String(digitalRead(BUTTON_PIN))
            );
            break;

        // TODO challenge:
        // Handle a new command called 'FIRMATA_REQUEST_PLAY_NOTE'
        //case FIRMATA_REQUEST_PLAY_NOTE:
            // We received a 'REQUEST_PLAY_NOTE' command.
            // This is a request from the raspberry pi
            // for the arduino to play a tone on the buzzer

            // TODO challenge:
            // We expect two parameters, the first being an integer
            // index into our array of notes (called TONE_LOOP_NOTES),
            // the second being the duration for the note in tenths
            // of seconds,
            // These arguments come from the argv array.
            // We want to call the play_tone function with the new tone
            // and millisecond duration
            
            // break;
    }
}

// Setup function that is called when the arduino first runs this code
void setup(){
    // set the LED and button pins to their appropriate input/output modes 
    pinMode(LED_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    // Initialise the firmata connection the raspberry pi
    firmata_init();
}

// Loop function that is called over after the arduino has run the
// setup function
void loop(){
    // First check if we have received any messages from the raspberry pi
    // that we need to process
    while(Firmata.available()) {
        Firmata.processInput();
    }
    // Then do everything else
    // In this case, if the 'alert' integer is set to a non-zero value
    // beep the buzzer.
    if(alert){
        occasionally_beep(2, 20);
    }
    // Sleep for a bit as we don't want to rush through the buzzer's
    // set of notes
    delay(200);
}
