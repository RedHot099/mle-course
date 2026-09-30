// Open a page in headless Chromium and poll a JavaScript expression until it
// returns a non-empty string, then print it. Author-only helper for checking
// lecture code that needs the network (Pyodide).
//
// Usage: node tools/browser_eval.mjs <url> <expression> [timeoutSeconds]
import { spawn } from "node:child_process";
import { setTimeout as sleep } from "node:timers/promises";

const [url, expression, timeoutArg] = process.argv.slice(2);
const timeout = Number(timeoutArg ?? 120) * 1000;
const port = 9333 + Math.floor(Math.random() * 500);
const browser = spawn("chromium", [
  "--headless=new", "--no-sandbox", "--disable-gpu",
  `--remote-debugging-port=${port}`, `--user-data-dir=/tmp/cdp-${port}`, "about:blank",
], { stdio: "ignore" });

async function targets() {
  for (let i = 0; i < 50; i++) {
    try {
      return await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    } catch {
      await sleep(200);
    }
  }
  throw new Error("Chromium did not start");
}

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
  const page = (await targets()).find((t) => t.type === "page");
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve) => socket.addEventListener("open", resolve));
  await call(socket, "Page.navigate", { url });
  const deadline = Date.now() + timeout;
  let value = "";
  while (Date.now() < deadline) {
    await sleep(1000);
    const result = await call(socket, "Runtime.evaluate", {
      expression, awaitPromise: true, returnByValue: true,
    });
    value = result?.result?.value;
    if (typeof value === "string" && value.length > 0) break;
  }
  console.log(value || "TIMEOUT");
  socket.close();
} finally {
  browser.kill();
}
