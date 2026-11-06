# Drones for Social Good

Drones for Social Good · Grade 9 · Technology for Good · PBL 2026–27 · The Indian International School, DSO

This README tells you what to fill in, how to run the project, and what is real and what is only a demo. Just want to run it? Jump to [How to install and run it](#how-to-install-and-run-it).

## Fill these in first

1. **The approval reference.** Replace `[Approval reference]` in `website/index.html`, line 322, with the reference your school gives you. If you do not have one yet, leave the placeholder as it is. Never make one up.
2. **The water sensor type.** Replace `[type]` in `website/index.html`, line 345, with the sensor you choose. See [Choosing a sensor](#choosing-a-sensor).
3. **The laptop's IP address.** Find it using [How to find the laptop's IP address](#how-to-find-the-laptops-ip-address), then write it here: `[Laptop IP]`. You do not edit it into any code. You type it into your phone's browser. It can change when the laptop reconnects to Wi-Fi, so check it again on demo day.

### Every placeholder and example value

Line numbers were correct when this was written. If they have moved, search the file for the text in the second column.

**Placeholders: the team must fill these in**

| What it is | Text in the file | File | Where |
|---|---|---|---|
| Approval reference | `[Approval reference]` | `website/index.html` | Line 322, Safety and ethics, "Approval first" card |
| Water sensor type | `[type]` | `website/index.html` | Line 345, Parts list, water sensor row |
| Number of drones | `[×N]` | `website/index.html` | Line 343, Parts list, generic camera drone row |
| Number of ESP boards | `[×N]` | `website/index.html` | Line 344, Parts list, ESP board row |
| Number of water sensors | `[×N]` | `website/index.html` | Line 345, Parts list, water sensor row |
| Number of wires | `[×N]` | `website/index.html` | Line 346, Parts list, wires row |
| Number of power banks | `[×N]` | `website/index.html` | Line 347, Parts list, power bank row |
| Number of laptops | `[×N]` | `website/index.html` | Line 348, Parts list, laptop row |
| Laptop's IP address | `[Laptop IP]` | `README.md` | Item 3 of the list above. Write it there. |

**`[Laptop IP]` in messages: do not edit these**

These are only messages telling people to use the real address.

| Text in the file | File | Where |
|---|---|---|
| `http://[Laptop IP]:` and "Remember to replace [Laptop IP]" | `receiver/server.py` | Lines 563, 564 and 565, messages printed when the server starts |
| `http://[Laptop IP]:5000` | `receiver/app.html` | Line 922, the note shown when notifications cannot work. It always says 5000, even if you use a different port. |

**Example values: the team must confirm or change these**

| What it is | Text in the file | File | Where |
|---|---|---|---|
| How often to check water tanks | `Example: once a week (team to confirm)` | `website/index.html` | Line 117, Inspection plan, Water tanks card |
| How often to check irrigation | `Example: once a week (team to confirm)` | `website/index.html` | Line 126, Inspection plan, Irrigation card |
| How often to check garden areas | `Example: twice a week (team to confirm)` | `website/index.html` | Line 135, Inspection plan, Garden areas card |
| How often to check rooftop tanks | `Example: once a month (team to confirm)` | `website/index.html` | Line 144, Inspection plan, Rooftop tanks card |

**Demo values: these have no brackets, but they are not real readings**

| What it is | Value | File | Where |
|---|---|---|---|
| Device name in every demo alert | `Drone-Scout-01` | `website/script.js` | Line 36, `EVENT_DEVICE` |
| Board name in every demo alert | `ESP (demo)` | `website/script.js` | Line 37, `EVENT_ESP_BOARD` |
| The tank the simulator reports | `Tank 2` | `website/script.js` | Line 38, `EVENT_TANK` |
| Where alerts say they came from | `simulator` | `website/script.js` | Line 64, `SENSOR_SOURCE` |
| The pretend sensor | `simulator.tank2Leaking` | `website/script.js` | Line 63, inside `readTankSensor()` |
| Time between automatic demo alerts | 60 to 120 seconds | `website/script.js`, `website/index.html` | `script.js` lines 30 and 31; `index.html` line 227 |
| Tank names | `Tank 1`, `Tank 2`, `Tank 3` | `receiver/server.py` | Line 41. If you rename a tank, also change `script.js` line 38 and `index.html` lines 94 to 96. |
| Where each tank is | On the roof, by the garden, by the irrigation line | `website/index.html` | Lines 94 to 96. This is the model's layout. Check it matches your school. |
| Campus size and layout in 3D | Positions and sizes in the code | `website/script.js` | Section 6, from line 685. These were chosen for the model. They are not measurements of your school. |

**Settings: these are choices, not measured results**

| What it is | Value | File | Where |
|---|---|---|---|
| Web port | `5000` | `receiver/server.py` | Line 63. You can change it without editing, using the `PORT` setting. |
| How long an event counts as recent | 15 minutes | `receiver/server.py` | Line 61 |
| Name length, message size, events returned, events stored | 64 characters, 16 KB, 100, 1000 | `receiver/server.py` | Lines 57 to 60 |
| How often pages refresh | 5 seconds | `website/script.js`, `receiver/app.html` | `script.js` line 33; `app.html` line 401 |

**Stand-ins used in this README only**

| What it is | Text | Where |
|---|---|---|
| A different port number | `5001` | [Port 5000 is busy](#port-5000-is-busy). Any free port will do. |
| The time in a message | `<ISO time>` | [Option A](#option-a-the-board-sends-the-alert-itself-the-easier-way). The board fills this in with the real time. |

## What this is

A Grade 9 project about using a cheap camera drone to inspect water tanks and gardens at school. It has three parts:

- **A scrolling 3D website.** It shows a model of a school campus, a generic drone and three water tanks. It also has a short film with no words.
- **A receiver.** This is a small Python program that runs on a laptop. It collects alert messages and saves them.
- **An app page.** The team opens this on a phone or laptop to see alerts, acknowledge them and clear them.

The alert is about one idea: when a water drop is detected at a tank, a message goes to the app, and that message always says whether it came from the simulator or a real sensor.

```
website/
  index.html        The words on the website
  styles.css        How it looks
  script.js         The 3D scene, the film and the simulator
receiver/
  server.py         The receiver program
  requirements.txt  Lists what Python needs to install (Flask)
  app.html          The app page
  data/             Made when the receiver runs. Alerts are saved in events.json
README.md           This file
```

## What is real and what is simulated

Nothing here measures a real tank. This project has **no measured results**: no litres saved, no percentages, no test scores.

| Part | Real or simulated? |
|---|---|
| The receiver, saving and sending alerts over Wi-Fi | **Real.** It really runs and really saves messages to `receiver/data/events.json`. |
| The app page, its feed, and the Acknowledge and Clear buttons | **Real.** They show and change the saved data. |
| The tank status (OK, Error, No data) | **Real calculation**, but it can only use the alerts it has received. |
| The water leak | **Simulated.** A simulator in the website pretends Tank 2 is leaking. |
| The water sensor | **Simulated.** No sensor is connected. `readTankSensor()` only reads the simulator. |
| The ESP board | **Simulated.** It is a labelled part on the 3D model. There is no code for a real board. |
| The drone | **A 3D model, shown for demonstration.** Nothing on this website controls a real drone. We do not assume a cheap drone has a programming interface. |
| The film | **Dramatised.** It is made from the 3D model. It is not footage of a flight or a leak. |
| The drop you see while scrolling the demo | **A preview.** Scrolling never sends an alert. |
| Tank 1 and Tank 3 | **Nothing reports them.** The simulator only reports Tank 2, so they normally show No data. |
| The "How often" values | **Examples** for the team to confirm. |

An alert is only sent in two ways: you press **Simulate drop**, or the automatic simulator fires. Every simulator alert is labelled "Simulator (demo)".

## How to install and run it

You only need to do steps 1 and 3 once. Python and the first install need internet.

A **terminal** is a window where you type commands. Windows calls it PowerShell or Terminal.

### Step 1: Install Python 3

You need Python 3.9 or newer. Check whether you already have it. Type this in a terminal:

| Windows | macOS and Linux |
|---|---|
| `py --version` | `python3 --version` |

If you see a version of 3.9 or higher, go to step 2. Otherwise:

**Windows**
1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the newest Python 3.
2. Run the installer. On the first screen, **tick "Add python.exe to PATH"**, then choose Install Now.
3. Close the terminal and open a new one, then check the version again.

If you are on a school laptop and it is blocked, ask your teacher or IT team.

**macOS**
1. Go to [python.org/downloads](https://www.python.org/downloads/), download the newest Python 3 and run the installer.
2. Open a new Terminal window and check the version again.

If you already use Homebrew, `brew install python` also works.

**Linux**

| Your Linux | Command |
|---|---|
| Ubuntu, Debian, Mint | `sudo apt update` then `sudo apt install python3 python3-venv` |
| Fedora | `sudo dnf install python3` |
| Arch | `sudo pacman -S python` |

### Step 2: Open a terminal in the `receiver` folder

- **Windows:** open the `receiver` folder in File Explorer, right-click an empty space, and choose **Open in Terminal**.
- **macOS:** in Finder, right-click the `receiver` folder and choose **New Terminal at Folder**. If you do not see it, open Terminal, type `cd ` with a space after it, drag the folder into the window, and press Enter.
- **Linux:** right-click in the `receiver` folder and choose **Open in Terminal**, or use `cd` to go there.

### Step 3: Install Flask (first time only)

Flask is the add-on that lets Python run a website. These commands make a private folder called `.venv` and put Flask inside it, so nothing else on the laptop changes.

**Windows**
```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```
If `py` is not found, use `python` instead of `py`.

**macOS and Linux**
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

### Step 4: Start the receiver (every time)

**Windows**
```powershell
.venv\Scripts\python server.py
```

**macOS and Linux**
```bash
.venv/bin/python server.py
```

It should print the website and app addresses. Flask also prints a warning that this is a development server. That is normal for a school demo, and it is a reminder not to put this on the public internet.

Keep this terminal open. **To stop the receiver, press Ctrl+C in it.**

### Step 5: Open the pages

On the laptop running the receiver:

| Page | Address |
|---|---|
| The 3D website | http://localhost:5000/ |
| The app | http://localhost:5000/app |

`localhost` means "this same computer".

On a phone or another laptop **on the same Wi-Fi**, put the laptop's IP address in place of `[Laptop IP]`:

| Page | Address |
|---|---|
| The 3D website | `http://[Laptop IP]:5000/` |
| The app | `http://[Laptop IP]:5000/app` |

Type `http://`, not `https://`. Always open the site through these addresses. If you double-click `index.html` instead, the alerts and the app link will not work.

### How to find the laptop's IP address

An IP address is the laptop's number on the Wi-Fi network. It looks like four groups of numbers with dots between them.

| Laptop | What to do |
|---|---|
| Windows | Type `ipconfig` in PowerShell. Under **Wireless LAN adapter Wi-Fi**, read the **IPv4 Address**. |
| macOS | Type `ipconfig getifaddr en0` in Terminal. If nothing appears, open System Settings, then Wi-Fi, then Details, and read the IP address. |
| Linux | Type `hostname -I`. The first address shown is usually the right one. |

### Try it out

1. Open the website and scroll to **Live alert demo**.
2. Press **Simulate drop**. A red badge should appear, and the line under the buttons should tell you whether the alert was sent.
3. Open the app page. You should see a red banner and a new row in the feed, marked **Simulator (demo)**.
4. Press **Acknowledge**, then **Clear**. Tank 2 should stop showing Error.

These steps were run once on the computer this project was built on, on 5 November 2026, using Windows 11, Python 3.12.10 and Flask 3.1.3, with the phone and laptop screen sizes imitated in a browser. They have not been tried on a real phone, over Wi-Fi from a second device, on macOS or on Linux, and browser notifications have not been tested. **Run them on your own laptop and phone before demo day**, and leave enough time to fix any problems.

### Port 5000 is busy

A port is like a door number on the laptop. On a Mac, AirPlay Receiver can use port 5000. If the receiver will not start, or a page will not load, choose another port with the `PORT` setting. `5001` is just an example:

| Laptop | Command |
|---|---|
| Windows | `$env:PORT = "5001"; .venv\Scripts\python server.py` |
| macOS and Linux | `PORT=5001 .venv/bin/python server.py` |

Then use 5001 instead of 5000 in every address.

### If something goes wrong

| What you see | What to try |
|---|---|
| `py` or `python` is not recognised | Install Python again, tick "Add python.exe to PATH", and open a new terminal. |
| Typing `python` opens the Microsoft Store | Use `py`, or install Python from python.org. |
| `No module named flask` | Use the `.venv` commands in step 4 exactly as written, from the `receiver` folder. |
| `py -m venv .venv` stops with an `ensurepip` error on Windows | The project folder's path is probably too long for Windows. Move the whole project to a shorter place, such as `Documents\drones`, delete `receiver\.venv`, and repeat step 3. |
| The phone cannot open the page | Check that both are on the same Wi-Fi, that you typed `http://`, and that the IP address is right. Then see the firewall note under [Known limits](#known-limits). |
| "Could not reach the receiver" on a page | The receiver is not running, or the Wi-Fi has dropped. Start it again. |
| "Not confirmed. The receiver did not answer in time." | The website waited 4 seconds and got no answer. The alert may still have arrived, so check the app before you send another. |
| The receiver says it could not read or save its data file | The file `receiver/data/events.json` may be damaged and could not be moved aside, or another program may be holding it. Close any program that has it open. Alerts already in the file are kept. When the file can be moved, a damaged copy is saved as `events.corrupt.json`, or `events.corrupt-<time>.json` if that name is taken. |
| Alerts appear without you pressing anything | That is the automatic simulator. It runs while the website is open. See [Known limits](#known-limits). |
| The 3D scene is missing | The 3D library comes from the internet and needs WebGL in the browser. Check the internet connection. The words, simulator and alerts are designed to keep working without it. |
| Tank 2 stays on Error | That is on purpose. Press Clear on the app page. |

To delete all alert history, stop the receiver and delete `receiver/data/events.json`. It is made again when needed. Only do this if nobody needs those records.

## Put the website online with GitHub Pages

GitHub Pages hosts web pages for free, so anyone with the link can open the 3D website. It cannot run Python, so the receiver and the `/app` page stay on your laptop.

| Part | On GitHub Pages | On your laptop with the receiver |
|---|---|---|
| 3D site, film, theme, scrolling | Works | Works |
| Simulate drop | Stays in the visitor's browser and disappears on reload | Sends a real message to the receiver |
| App panel on the site | Shows only that browser's demo alerts | Shows live data |
| Full app at `/app` | Not available, so the button is removed | Works |
| Real sensor alerts | Not available | Works |

The site switches by itself. A page opened over `https://` is treated as the online copy, and it says so in the app panel. To preview that version on your laptop, add `?online-copy=1` to the address.

**Before you publish:** the page is public, and it shows your school's name. Ask your teacher first, and fill in or decide about every placeholder at the top of this file, because visitors will see them.

### Steps

1. Sign in at [github.com](https://github.com), or create an account there.
2. Press **+** at the top right, then **New repository**. Give it a name such as `drones-for-social-good`, choose **Public**, and press **Create repository**.
3. On the new repository's page, press **uploading an existing file**.
4. Open the `website` folder and drag these three files in: `index.html`, `styles.css` and `script.js`. Drag the files themselves, not the folder, so `index.html` ends up at the top level. Press **Commit changes**.
5. Open **Settings**, then **Pages** in the left menu.
6. Under **Build and deployment**, set **Source** to **Deploy from a branch**. Set the branch to **main** and the folder to **/ (root)**, then press **Save**.
7. Wait a minute or two and refresh that page. Your link appears at the top. It looks like `https://YOUR-USERNAME.github.io/drones-for-social-good/`.

To change the site later, upload the changed file to the same repository in the same way. It updates within a few minutes.

If the link shows a 404 page, check that `index.html` is at the top level of the repository and not inside a folder.

## The status rules

The app shows one status for each tank. The rules are in `receiver/server.py`, in `build_tank_status`.

| Status | When it shows |
|---|---|
| **Error** | The tank has at least one error alert that nobody has cleared. **This stays however old the alert is**, because a leak must not disappear just because 15 minutes went by. |
| **OK** | The tank has no uncleared errors, and at least one event arrived in the last 15 minutes. |
| **No data** | The tank has no uncleared errors, and no event arrived in the last 15 minutes. |

"The last 15 minutes" goes by the time the receiver got the event, not the time on the sender's clock.

What the buttons do:

- **Acknowledge** means "someone has seen this". The tank stays on Error, marked as acknowledged. A tank only counts as acknowledged when all its uncleared errors are acknowledged.
- **Clear** means "this has been dealt with". It also acknowledges the alert. The alert stays in the history, looking faded.

So Tank 2 might go: No data, then Error after a drop, then Error (acknowledged), then OK after Clear, then No data once 15 minutes have passed with no new event.

**Be careful with what OK means.** The receiver only knows about messages it has received. OK does not mean someone checked the tank, and No data does not mean the tank is safe. It only means no message arrived.

## How to replace the simulator with a real sensor

Right now, in `website/script.js`, lines 55 to 64:

```js
const simulator = { tank2Leaking: false };
function readTankSensor() { return simulator.tank2Leaking; }
const SENSOR_SOURCE = "simulator";
```

`readTankSensor()` answers one question: is there a drop? `true` means yes. The website only sends an alert if the answer is `true`. `SENSOR_SOURCE` is the label on the alert. The rule is that real and simulator alerts use the same message format, and the label must always be truthful.

There is no code here for any particular board. The team writes that part with their teacher, for the board they have.

### Choosing a sensor

| Sensor | What it notices |
|---|---|
| Flow sensor | Water moving through a pipe |
| Float switch | The water level in a tank changing |
| Drip sensor | Drops or wetness where it is placed |

Each one notices something different, so test it on your own tank before you trust it. Then fill in `[type]`.

### Option A: the board sends the alert itself (the easier way)

The ESP board at the tank reads the sensor. When it detects a drop, it sends this to `http://[Laptop IP]:5000/events` as a POST request, with the header `Content-Type: application/json`:

```json
{"device":"Drone-Scout-01","esp_board":"ESP (demo)","tank":"Tank 2","event":"WATER_DROP_DETECTED","severity":"error","source":"real_sensor","timestamp":"<ISO time>"}
```

- Change `device` and `esp_board` to your real names, up to 64 characters each.
- `tank` must be `Tank 1`, `Tank 2` or `Tank 3`.
- `timestamp` must be a real date and time, in ISO 8601 format, so the board has to know the time. A time service on the internet can give it that.
- The receiver answers `{"ok": true}` if it accepts the message. If not, it gives the reason in plain English.

You can leave `readTankSensor()` and `SENSOR_SOURCE` alone with this option, because the board labels its own alerts. For real use, only open `/app`. If the website is open too, its simulator keeps sending alerts labelled as simulator.

**Test the receiver without a board.** These send one alert labelled as simulator, so it cannot be mistaken for a real detection. Run them in a second terminal while the receiver is running. You should get a reply saying `ok` is true.

Windows PowerShell:
```powershell
$body = @{ device="Drone-Scout-01"; esp_board="ESP (demo)"; tank="Tank 1"; event="WATER_DROP_DETECTED"; severity="error"; source="simulator"; timestamp=(Get-Date).ToUniversalTime().ToString("s") + "Z" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/events" -Method Post -ContentType "application/json" -Body $body
```

macOS and Linux:
```bash
curl -X POST http://localhost:5000/events -H "Content-Type: application/json" -d "{\"device\":\"Drone-Scout-01\",\"esp_board\":\"ESP (demo)\",\"tank\":\"Tank 1\",\"event\":\"WATER_DROP_DETECTED\",\"severity\":\"error\",\"source\":\"simulator\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
```

### Option B: the website reads the sensor

A web page cannot read a wire, so your own code must bring the reading to the page. The page also has to stay open the whole time. That is why Option A is easier. If you use this option, make **all** of these changes in `website/script.js`:

1. **Change `readTankSensor()` (line 63)** so it gives a quick `true` or `false` from the real sensor:
   ```js
   let latestReading = false;   // Your code must keep this up to date from the real sensor.
   function readTankSensor() { return latestReading; }
   ```
2. **Change `SENSOR_SOURCE` (line 64)** to `"real_sensor"`.
3. **Turn the simulator off.** Delete `wireSimulatorButtons();` from `startSite()` (line 2839).

   **Do not skip this.** If you do, the timer keeps running, and the red badge will claim a drop from a "real sensor" when nothing happened.
4. **Call `checkSensorAndSend()`** when the reading changes from `false` to `true`. It sends one alert every time it is called and the reading is `true`, so calling it on a timer would flood the feed.
5. **Update the names and words.** Change `EVENT_DEVICE`, `EVENT_ESP_BOARD` and `EVENT_TANK` (lines 36 to 38) and the "demo alert" message (line 91). In `website/index.html`, remove the two buttons (lines 223 and 224) and rewrite the demo section's words (lines 212, 216, 220 and 226 to 228), which describe the simulator.

The red badge and the 3D drip come from `simulateDrop()`, which is now off. Alerts still reach the app. Add your own code if you want those visuals back.

## The reduce-motion testing switch

Some people feel unwell from moving pages, so devices have a "reduce motion" setting. The website follows that setting. To test it without changing your device, add `?reduce-motion=1` to the address:

- http://localhost:5000/?reduce-motion=1
- `http://[Laptop IP]:5000/?reduce-motion=1`

To turn it off, remove `?reduce-motion=1` and load the page again. The code only checks that the word is there, so `?reduce-motion=0` also turns it **on**.

With it on, you should see:

- No pinned sections. All the cards are stacked in a plain page.
- No camera moves or zoom. The view jumps to one fixed shot for each section, and the rotors stay still.
- No falling drip. A still drop sits below Tank 2 while the leak is on.
- Four still frames instead of the film, moved with the **Previous** and **Next** buttons.

The alerts work as usual. This switch is for the website only, not `/app`.

## Known limits

- **Plug the laptop in for your demo.** On battery, especially when it is low, the browser can limit pages to about 30 frames a second. The film looks less smooth, and the site cannot change this.
- **The site protects its own speed.** If frames stay slow, it draws fewer pixels and updates shadows less often, so the picture can look a little softer on a slower computer. On the lowest level it also leaves out the film grain.
- **The film has no edge blur.** It was too slow on ordinary laptops, so a soft dark fade at the edges of the picture does that job.
- **There is no login.** Anyone on the same Wi-Fi who knows the address can send or clear events. They could also send a fake alert labelled "Real sensor", because the receiver trusts the label it is given. Only run this on a network you trust, and only during your demo.
- **Browser notifications need HTTPS or localhost.** They can work on the laptop at `http://localhost:5000/app`, but **they will not work on a phone over plain `http://`**. The app page explains this and keeps working, so keep it open and watch the banner and feed. Notifications also only come while the app page is open.
- **Windows firewall.** The first time the receiver starts, Windows may ask whether to allow Python. Allow it on **private networks only**. If you missed the question, or the phone still cannot connect, open Windows Security, then Firewall & network protection, then "Allow an app through firewall", and tick Private for Python. Also set your Wi-Fi as a private network in Windows Settings. On a school laptop, you may need an adult or the IT team for this.
- **macOS AirPlay can use port 5000.** Use the `PORT` setting. See [Port 5000 is busy](#port-5000-is-busy).
- **School Wi-Fi may block phones from reaching laptops,** even when both are connected. If nothing else helps, ask the IT team, or ask your teacher about using a phone hotspot instead.
- **The laptop must stay on.** If it sleeps or the receiver stops, alerts cannot arrive. Alerts are only stored on this laptop.
- **The automatic simulator keeps going.** Every open copy of the website runs its own simulator, so two open copies send about twice as many demo alerts. **Reset** stops the leak on that page, but the timer starts again and will fire later. Close the website to stop it. The app page does not run the simulator.
- **Internet is needed for the 3D library and fonts,** which load from the web. Older phones may find the 3D scene slow. If so, use `/app` on the phone.
- **The history can grow.** Above 1000 events, the oldest cleared events are removed. Uncleared alerts are never removed, so clear them when you are done.

## A note for the teacher

**The sensor sits at the tank, not on the drone.** A flow sensor, float switch or drip sensor has to be physically at the tank or pipe to detect anything. In a real setup, it would connect to an ESP board near the tank, and that board would send the alert over Wi-Fi. The drone's real job is the camera inspection, flown by an adult pilot with a spotter.

**The ESP board on the drone is a demo part.** It appears on the 3D model to help explain the idea. We are not suggesting anyone fit one to a real drone. **Mounting anything on a cheap drone may affect its weight and balance**, and so how safely it flies.

Before any real work, please check these:

- Any flight needs the school's approval and must follow local drone rules. The website's `[Approval reference]` is there for this.
- Faces must be blurred before any photos are shared.
- An adult should check any sensor wiring, and electronics should be kept away from water.
- Please help students present this as a demo. It shows an idea, and there are no measured results to report.
