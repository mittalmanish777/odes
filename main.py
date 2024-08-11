from flask import *
import uuid
import ODES as odes
import os
import csv
import cv2


app = Flask(__name__)


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/images', methods=['GET'])
def show_image_preview():
    original_image = request.args.get('original-image')
    annotated_image = request.args.get('annotated-image')

    results = "<table style=\"width:80%\" class=\"content\" border=\"1\">"
    results += "<tr>"
    results += "<th>Original Image</th>"
    results += "<th><div class=\"img-magnifier-container\"><img id=\"orig-img\" src=\"" + original_image + "\" alt=\"Original\"></div></th>"

    results += "</tr>"

    results += "<tr>"
    results += "<th>Annotated Image</th>"
    results += "<th><div class=\"img-magnifier-container\"><img id=\"ann-img\" src=\"" + annotated_image + "\" alt=\"Annotated\"></div></th>"
    results += "</tr>"
    results += "</table>"

    return render_template("results.html", table_data=results)


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':

        # Get the list of files from webpage
        files = request.files.getlist("file")
        image_dir = str(uuid.uuid4())

        image_dir = os.path.join("static", "uploadedImages", image_dir)
        os.makedirs(image_dir, exist_ok=True)

        thumbnail_dir = os.path.join(image_dir, "thumbnails")
        os.makedirs(thumbnail_dir, exist_ok=True)

        # Iterate for each file in the files List, and Save them
        for file in files:
            image_name = image_dir + "/" + file.filename
            file.save(image_name)
            im = cv2.imread(image_name)
            im = cv2.resize(im, (120, 120))
            cv2.imwrite(image_dir + "/thumbnails/" + f"t-{file.filename}-120.jpg", im)

        odes.executeODES(image_dir, True)

        app.config['IMAGE_FOLDER'] = image_dir

        output_csv_path = os.path.join(image_dir, 'results.csv')
        file = open(output_csv_path, 'r')
        csv_reader = csv.reader(file)

        results = "<table style=\"width:80%\" class=\"content\" border=\"1\">"

        row_num = 0
        for row in csv_reader:
            results += "<tr>"

            col_num = 0
            image_name = ""
            for col in row:

                if col_num == 0:
                    image_name = col
                    col_num += 1

                if row_num == 0:
                    results += "<th style=\"width:5%\">" + col + "</th>"
                else:
                    results += "<td style=\"width:5%\">" + col + "</td>"

            if row_num == 0:
                results += "<th style=\"width:10%\">Original Image</th>"
                results += "<th style=\"width:10%\">Annotated Image</th>"
                row_num += 1
            else:
                original_thumbnail = f"t-{image_name}-120.jpg"
                original_thumbnail = os.path.join(app.config['IMAGE_FOLDER'], "thumbnails", original_thumbnail)
                original_image = os.path.join(app.config['IMAGE_FOLDER'], image_name)

                annotated_thumbnail = f"t-annotated_{image_name}-120.jpg"
                annotated_thumbnail = os.path.join(app.config['IMAGE_FOLDER'], "annotated_images", "thumbnails",
                                               annotated_thumbnail)
                annotated_image = os.path.join(app.config['IMAGE_FOLDER'], "annotated_images",
                                               "annotated_" + image_name)

                results += ("<td><a href=\"images?original-image=" + original_image + "&annotated-image=" + annotated_image + "\" target=\"preview\"> <img src=\"" + original_thumbnail
                            + "\" alt=\"Original\"></a></td>")

                results += ("<td><a href=\"images?original-image=" + original_image + "&annotated-image=" + annotated_image + "\" target=\"preview\"> <img src=\"" + annotated_thumbnail
                            + "\" alt=\"Annotated\"></a></td>")
            results += "</tr>"

        results += "</table>"
        return render_template("results.html", table_data=results)


if __name__ == '__main__':
    app.run(debug=True)
