#include <Hx711.h>

/* sample for digital weight scale of hx711, display with a HD44780 liquid crtstal monitor
 *
 * hardware design: syyyd
 * available at http://syyyd.taobao.com
 *
 * library design: Weihong Guan (@aguegu)
 * http://aguegu.net
 *
 * library host on
 * https://github.com/aguegu/Arduino
 */

// Hx711.DOUT - pin #A1
// Hx711.SCK - pin #A0

Hx711 scale(A1, A0);

void setup() {

  Serial.begin(9600);
  
  // calibration
  scale.setScale(-333.07);

}

void loop() {
  Serial.println(scale.getGram(), 1);
  delay(2000);
}
