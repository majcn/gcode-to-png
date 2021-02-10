const puppeteer = require("puppeteer");
const fileUrl = require("file-url");
const fs = require("fs");
const glob = require("glob");
const path = require("path");

async function getGCodeFiles(dirName) {
  return new Promise((resolve, reject) => {
    glob(dirName + "/**/*.gcode", {}, (err, files) => {
      return resolve(files);
    });
  });
}

const inputDirName = path.join(__dirname, "input");
const outputDirName = path.join(__dirname, "output");

async function doWithPage(page) {
  const gcodeFiles = await getGCodeFiles(inputDirName);

  for (let gcodeFile of gcodeFiles) {
    const gcode = fs.readFileSync(gcodeFile, "utf-8");

    const canvasDataUrl = await page.evaluate((x) => {
      gcodePreview.clear();
      gcodePreview.startLayer = 2;
      gcodePreview.processGCode(x);
      return document.getElementById("renderer").toDataURL();
    }, gcode);

    const outputFileName =
      outputDirName +
      gcodeFile.replace(inputDirName, "").replace(".gcode", ".png");

    fs.mkdirSync(outputFileName.split("/").slice(0, -1).join("/"), {
      recursive: true,
    });

    fs.writeFileSync(
      outputFileName,
      canvasDataUrl.replace(/^data:image\/png;base64,/, ""),
      "base64"
    );
  }
}

async function main() {
  const browser = await puppeteer.launch({ defaultViewport: null });
  const page = await browser.newPage();

  await page.goto(fileUrl("GCodeRenderer.html"));
  await doWithPage(page);
  await browser.close();
}

main();
