# robot-sim — the hardware bridge (simulated)

A tiny REST service that pretends to be a robot, so the Freehold control panel
works with **zero hardware**. Two endpoints:

- `GET /state` → `{x, y, heading, speed, distance_cm, temp_c, battery, cmd}`
- `POST /drive` → `{action: forward|back|left|right|stop, speed}`

## Going real (on a Raspberry Pi)
Replace this container with one that talks to actual hardware — read an
HC-SR04 on GPIO for `distance_cm`, drive an L298N for the motors — and keep the
**same two endpoints**. The Freehold app never changes: it only knows the REST
contract. That's the whole point — the robot is just a plugged-in package.
