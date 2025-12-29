## Project summary
I built a smart thermostat prototype. The goal was to make the basic thermostat features work first, before adding cloud features. The system keeps a temperature setpoint, switches between OFF, HEAT, and COOL, shows info on an LCD, uses LEDs to show heating/cooling, and sends status data over UART to simulate sending data to a server.

## What problem it was solving
SysTec needed a working thermostat prototype that could later connect to the cloud. This project showed that the core logic works: the device can take temperature input, react correctly, show the user what is happening, and output structured data for reporting.

## What I did particularly well
I made a clear state machine and connected it directly to the hardware behavior. I also made the system easy to verify: the LCD updates consistently, the LED behavior matches the rules, and the UART output uses a simple CSV format.

## Where I could improve
I could improve hardware testing earlier, especially with wiring limits and making sure all parts (buttons and sensor) are available before final integration. Next time I would also add a small automated test for the state machine logic so I can confirm behavior even when hardware is limited.

## Tools and resources I added to my support network
I improved how I document wiring and debugging steps. I also got better at using library documentation (GPIOZero and Adafruit CircuitPython) and writing small test scripts to make sure each peripheral works before combining everything.

## Transferable skills
This project improved skills that transfer to other embedded and systems projects: working with GPIO, using I2C and UART, handling button input with callbacks, building state machines, and designing around hardware limits.

## How I made it maintainable, readable, and adaptable
I kept the code organized into clear sections (inputs, state machine, outputs), and separated state logic from hardware details when possible. I added comments to explain intent, and I designed the temperature input so it can use a real I2C sensor or a simulated value for testing and demos. This would make it easier to change hardware later without rewriting the whole project.
