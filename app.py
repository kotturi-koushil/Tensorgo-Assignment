from flask import Flask, render_template, request, redirect, url_for, send_file
import os
import cv2

app = Flask(__name__)

uploadingfoder = "uploads"
outputfolder = "processed"

app.config["uploadingfolder"] = uploadingfoder
app.config["outputfolder"] = outputfolder


def sdtohd(inputpath, outputpath):
    inputvideo = cv2.VideoCapture(inputpath)
    width = int(inputvideo.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(inputvideo.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = inputvideo.get(cv2.CAP_PROP_FPS)

    outputvideo = cv2.VideoWriter(
        outputpath, cv2.VideoWriter_fourcc(*"mp4v"), fps, (1280, 720)
    )

    while inputvideo.isOpened():
        ret, frame = inputvideo.read()
        if not ret:
            break

        convertedframe = conversion(frame)
        afterconversion = cv2.resize(
            convertedframe, (1280, 720), interpolation=cv2.INTER_CUBIC
        )
        qualityframe = qualityimprover(afterconversion)
        finalframe = afterprocess(qualityframe)

        outputvideo.write(finalframe)

    inputvideo.release()
    outputvideo.release()


def conversion(frame):
    noiseremoved = cv2.bilateralFilter(frame, 9, 75, 75)
    return noiseremoved


def qualityimprover(frame):
    qualityframe = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_CUBIC)
    return qualityframe


def afterprocess(frame):
    sharpframe = cv2.GaussianBlur(frame, (0, 0), 3)
    sharpframe = cv2.addWeighted(frame, 1.5, sharpframe, -0.5, 0)
    return sharpframe


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def uploadfile():
    if "file" not in request.files:
        return redirect(request.url)
    file = request.files["file"]
    if file.filename == "":
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config["uploadingfolder"], file.filename)
        file.save(filepath)
        outputvideopath = os.path.join(app.config["outputfolder"], "hd" + file.filename)

        sdtohd(filepath, outputvideopath)
        return redirect(url_for("downloadfile", filename="hd" + file.filename))


@app.route("/download/<filename>")
def downloadfile(filename):
    return send_file(
        os.path.join(app.config["outputfolder"], filename), as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)
