// Screenshot one element of a page in headless Chromium.
// Usage: node tools/browser_shot.mjs <url> <css selector> <out.png> [dark]
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
import { setTimeout as sleep } from "node:timers/promises";

const [url, selector, out, theme] = process.argv.slice(2);
const port = 9833 + Math.floor(Math.random() * 500);
const browser = spawn("chromium", [
  "--headless=new", "--no-sandbox", "--disable-gpu", "--window-size=1280,1600",
  `--remote-debugging-port=${port}`, `--user-data-dir=/tmp/cdp-${port}`, "about:blank",
], { stdio: "ignore" });

let id = 0;
function call(socket, method, params = {}) {
  const message = { id: ++id, method, params };
  return new Promise((resolve) => {
    const onMessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.id === message.id) {
        socket.removeEventListener("message", onMessage);
        resolve(data.result);
      }
    };
    socket.addEventListener("message", onMessage);
    socket.send(JSON.stringify(message));
  });
}

try {
  let targets;
  for (let i = 0; i < 50 && !targets; i++) {
    try {
      targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    } catch {
      await sleep(200);
    }
  }
  const page = targets.find((t) => t.type === "page");
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve) => socket.addEventListener("open", resolve));
  await call(socket, "Page.navigate", { url });
  await sleep(1500);
  if (theme === "dark") {
    await call(socket, "Runtime.evaluate", { expression: "document.getElementById('theme-toggle')?.click()" });
    await sleep(300);
  }
  const box = await call(socket, "Runtime.evaluate", {
    expression: `(() => { const n = document.querySelector(${JSON.stringify(selector)}); n.scrollIntoView(); const r = n.getBoundingClientRect(); return JSON.stringify({x: r.x + scrollX, y: r.y + scrollY, width: r.width, height: r.height}); })()`,
    returnByValue: true,
  });
  const clip = { ...JSON.parse(box.result.value), scale: 1 };
  const shot = await call(socket, "Page.captureScreenshot", { format: "png", clip, captureBeyondViewport: true });
  writeFileSync(out, Buffer.from(shot.data, "base64"));
  console.log(out);
  socket.close();
} finally {
  browser.kill();
}
