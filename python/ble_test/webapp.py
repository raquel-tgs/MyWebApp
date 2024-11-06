# https://jsfiddle.net/4gnXL/2/
# credits https://blog.miguelgrinberg.com/post/beautiful-flask-tables-part-2
#
import sys
import os
import time
import numpy as np
from flask import Flask, render_template, request, abort, jsonify, redirect, url_for, send_file, Response, render_template_string
import pandas as pd
import datetime
import threading
import shutil
import json
from io import StringIO
import shutil
import math
#import certgen_py

import logging

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    q = StringField('Search')
    submit = SubmitField('Search')

app = Flask(__name__)

image_folder = os.path.join('static', 'images')
report_folder = os.path.join('static', 'reports')
cert_folder = os.path.join('static', 'certs')
 
app.config['IMAGE'] = image_folder
app.config['REPORT'] = report_folder
app.config['CERT'] = cert_folder
app.config['SECRET_KEY'] = 'j4f894848wa4lh84who84wo'

@app.route('/')
def index():
    if isLoggedIn:
        return redirect(url_for('tag_table'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_role
    global isLoggedIn
    if request.method == 'GET':
        return render_template('landing_page.html')
    else:
        username = request.form['username']
        password = request.form['password']
        user_role = request.form['role']
        if username == admin_username and password == admin_password:
            isLoggedIn = True
            return redirect(url_for('tag_table'))
        else:
            isLoggedIn = False
            error = 'Invalid username or password'
            return render_template('landing_page.html', error=error)

currentPage = 1
perPage = 10

@app.route('/tagtable', methods=['GET', 'POST'])
def tag_table():
    global modalOpen
    global page_selected
    global operation
    form = SearchForm()
    data_json = json.loads(data.to_json(orient="records"))
    query = ''
    tags=[]
    if form.validate_on_submit():
        query = form.q.data
        for tag in data_json:
            if query.lower() in tag['mac'].lower() or query.lower() in tag['tag_id'].lower() or query.lower() in tag['name'].lower() or query.lower() in tag['color'].lower():
                tags.append(tag)
    else:
        tags = data_json
    page_selected="tag_table"
    currentPage = request.args.get('page', 1, type=int)
    first = ((perPage*currentPage)-perPage)
    last = perPage*currentPage
    totalPages = math.ceil(len(tags)/perPage)
    pagesArr = [x + 1 for x in range(totalPages)]
    # return render_template('editable_table.html', 
    return render_template('editable_table.html.j2', 
        tags = tags[first : last], 
        totalTags = len(tags), 
        first = first + 1, 
        last = last if last <= len(tags) else len(tags), 
        current = currentPage, 
        pages = pagesArr, 
        prev = (currentPage - 1 if currentPage > pagesArr[0] else pagesArr[0]) if len(tags) > 1 else 1, 
        next = (currentPage + 1 if currentPage < pagesArr[-1] else pagesArr[-1]) if len(tags) > 1 else 1, 
        userRole = user_role, 
        modalOpen = modalOpen, 
        operation = operation,
        form = form)

@app.route('/api/image', methods=['GET', 'POST'])
def get_set_image():
    if request.method == 'GET':
        return '', 204
    else:
        certificate_id = request.form['certificate_id']
        mac = request.form['mac']
        img = request.files['image']
        if img.filename:
            extension = img.filename.split('.')[1]
            img.filename = certificate_id+'.'+extension
            img.save(os.path.join(app.root_path, app.config['IMAGE'], img.filename))
            shutil.copy(os.path.join(app.root_path, app.config['IMAGE'], img.filename), os.path.join(localpath, 'images', img.filename))
            cloud_data = pd.read_csv(localpath+"cloud.csv")
            cloud_json = json.loads(cloud_data.to_json(orient="records"))
            for tag in cloud_json:
                if tag['mac'] == mac:
                    tag['asset_images_file_extension'] = extension.upper()
            updated_cloud_string = json.dumps(cloud_json)
            updated_cloud = pd.read_json(StringIO(updated_cloud_string))
            updated_cloud.to_csv(localpath+"cloud.csv")
            return redirect(url_for('edit_tag_details', tag_mac = mac))
        else:
            return redirect(url_for('edit_tag_details', tag_mac = mac))

@app.route('/tag-details/<tag_mac>')
def tag_details(tag_mac):
    tag_data = get_tag_by_mac(tag_mac)
    image = os.path.join('images', f"{tag_data['certificate_id']}.{tag_data['asset_images_file_extension'].lower()}")
    return render_template('tag_details.html', tag = tag_data, image = image)

@app.route('/view/report/<tag_mac>')
def view_tag_report(tag_mac):
    report = 'reports/ADDF-23.pdf'
    return render_template('view_report.html', report = report, mac = tag_mac)

@app.route('/view/cert/<tag_mac>')
def view_tag_cert(tag_mac):
    cert = generate_pdf(tag_mac)
    print(cert)
    return render_template('view_cert.html', cert = cert, mac = tag_mac)

def generate_pdf(mac):
    tag = get_tag_by_mac(mac)
    logo = os.path.join(app.root_path, app.config['IMAGE'], 'logo.jpg')
    asset = os.path.join(app.root_path, app.config['IMAGE'], 'rodpump.jpg')
    sig = os.path.join(app.root_path, app.config['IMAGE'], 'signature.jpg')
    path = os.path.join(app.root_path, app.config['CERT'], f'{mac}.pdf')
    try:
        pdf = certgen_py.Asset(
            company_name = tag['certification_company_name'],
            company_id = tag['certification_company_id'],
            certificate_id = tag['certificate_id'],
            expiration_date = "2023-12-31", #tag['expiration_date'],
            test_type = tag['test_type'],
            asset_id = tag['asset_id'],
            asset_type = "Widget", #tag['asset_type']
            logo = logo,
            asset_image = asset,
            signature = sig
        )
        pdf.gen_cert(path)    
        return f'certs/{mac}.pdf'
    except:
        return 'certs/certification.pdf'

def get_tag_by_mac(mac):
    data_json = json.loads(data.to_json(orient="records"))
    tag_data = None
    for tag in data_json:
        if tag['mac'] == mac:
            tag_data = tag
    return tag_data

@app.route('/tag-details/edit/<tag_mac>')
def edit_tag_details(tag_mac):
    tag_data = get_tag_by_mac(tag_mac)
    image = ''
    if tag_data and tag_data['certificate_id'] and tag_data['asset_images_file_extension']:
        image = os.path.join('images', f"{tag_data['certificate_id']}.{tag_data['asset_images_file_extension'].lower()}")
    return render_template('edit_tag_details.html', tag = tag_data, image = image)

@app.route('/upload_file')
def upload_file():
    file = request.files['file']
    file.save(os.path.join(app.root_path, app.config['REPORT'], file.filename))
    return '', 204

@app.route('/api/canceloperation_web', methods=['POST'])
def canceloperation_web():
    canceloperation_back()
    checkstatus()
    return redirect(url_for('tag_table'))

@app.route('/api/canceloperation', methods=['POST'])
def canceloperation():
    canceloperation_back()
    checkstatus()
    return redirect(url_for(page_selected))  # 'page_configuration'))

def canceloperation_back():
    # data = pd.read_csv("scan.csv")
    global status
    global  operation
    global updatedix
    global mac_filter
    global webcancel
    global modalOpen
    global page_selected
    modalOpen=False
    if status=="Disabled":

        if operation == 'Scan':
            file_path = localpath + "scan.csv"
            file_path_copy = localpath + "scan_copylastscan.csv"
            if os.path.exists(file_path_copy):
                try:
                    try:
                        # Copy file and metadata, and overwrite if it already exists
                        shutil.copy(file_path_copy, file_path )
                        print(f"File copied successfully from {file_path} to {file_path_copy}")
                    except Exception as e:
                        print(f"Error occurred: {e}")

                    os.remove(file_path_copy)
                    print(f"File '{file_path_copy}' has been deleted.")
                    # return True
                except Exception as e:
                    print(f"An error occurred while deleting the file: {e}")
                    # return False
            else:
                print(f"File '{file_path_copy}' does not exist.")
                pd.DataFrame(columns=columnIds).to_csv(file_path,index=False)

        elif operation == 'Update':
            # pass # do something else
            file_path = localpath + "scan_update.csv"
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"File '{file_path}' has been deleted.")
                    # return True
                except Exception as e:
                    print(f"An error occurred while deleting the file: {e}")
                    # return False
            else:
                print(f"File '{file_path}' does not exist.")
            updatedix = []


        elif operation == 'Location':
            # pass # do something else
            file_path = localpath + "scan_location.csv"
            file_path_copy = localpath + "scan_location_copylastlocation.csv"
            if os.path.exists(file_path_copy):
                try:
                    try:
                        # Copy file and metadata, and overwrite if it already exists
                        shutil.copy(file_path_copy , file_path)
                        print(f"File copied successfully from {file_path_copy} to {file_path}")
                    except Exception as e:
                        print(f"Error occurred: {e}")

                    os.remove(file_path_copy)
                    print(f"File '{file_path_copy}' has been deleted.")
                    # return True
                except Exception as e:
                    print(f"An error occurred while deleting the file: {e}")
                    # return False
            else:
                print(f"File '{file_path_copy}' does not exist.")
                columnIds_location = ["tag_mac", "out_prob", "out_prob_k", "anchors", "result", "x", "y"]
                pd.DataFrame(columns=columnIds_location).to_csv(file_path,index=False)

        else:
            pass # unknown
            # return render_template("editable_table.html")
        webcancel = True

    #return render_template("editable_table.html")
    #return redirect(url_for(page_selected))#'page_configuration'))

# @app.route("/datatype_dropdown", methods=["POST"])
# def datatype_dropdown():
#     global page_datatype
#     data = request.get_json()
#     page_datatype = data.get("selected_value")
#
#     # Process the selected value and prepare a response
#     response_message = f"You selected: {page_datatype}"
#
#     # Return a JSON response to the frontend
#
#     if (page_datatype=="Base Data"):
#         # page_configuration()
#         return page_configuration()
#     elif (page_datatype == "Detail Data"):
#         # page_configuration_detail()
#         return   page_configuration_detail()
#     elif (page_datatype == "Configuration Data"):
#         # page_configuration_configuration()
#         return page_configuration_configuration()
#
#     # return jsonify({"message": response_message})

# @app.route("/datatype_dropdown/page_configuration")
# def datatype_dropdown():
#     global page_datatype
#     #data = request.get_json()
#     # Return a JSON response to the frontend
#     return page_configuration()
#
# @app.route("/datatype_dropdown/page_configuration_configuration")
# def datatype_dropdown_configuration():
#     global page_datatype
#     #data = request.get_json()
#     # Return a JSON response to the frontend
#     return page_configuration_configuration()
#
# @app.route("/datatype_dropdown/page_configuration_detail")
# def datatype_dropdown_detail():
#     global page_datatype
#     #data = request.get_json()
#     # Return a JSON response to the frontend
#     return page_configuration_detail()

@app.route('/api/data')
def data_api():
    # data = pd.read_csv("scan.csv")
    global data
    global reloadpage

    reloadpage="False"

    # search filter
    search = request.args.get('search')
    if search:
        # query = query.filter(db.or_(
        #     User.name.like(f'%{search}%'),
        #     User.email.like(f'%{search}%')
        # ))
        ix1=data['mac'].str.contains(search)
        ix2=data['tag_id'].str.contains(search)
        ix3=data['asset_id'].str.contains(search)
        # data_res=data[(ix1 & ix2 & ix3)]
        ix=(ix1 | ix2 | ix3)
    else:
        ix =[True for x in list(data.index)]
    # total = query.count()
    total = data[ix].shape[0]

    # sorting
    sort = request.args.get('sort')
    if sort:
        order = []
        for s in sort.split(','):
            direction = s[0]
            name = s[1:]
            if name not in ['mac', 'tag_id', 'asset_id']:
                name = 'mac'
            # col = getattr(User, name)
            if direction == '-':
                # col = col.desc()
                data=data[ix].sort_values(by=[name], ascending=False)
            else:
                data=data[ix].sort_values(by=[name],ascending=True)
            # order.append(col)
        # if order:
        #     query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        # query = query.offset(start).limit(length)
        data_res=data.loc[data.index.isin(list(data[ix].index)[start:start+length])]
        data_res=data_res.fillna("")

    return {
        # 'data': [data.loc[ix].to_json() for ix in data.index],
        'data': [data_res.loc[ix].to_dict() for ix in data_res.index],
        'total': total,
    }

@app.route('/api/gateway', methods=['POST'])
def gateway():
    selected_value = request.form.get('gateway_selection')
    print("zone {}".format(selected_value))
    return '', 204

@app.route('/checkbox_select', methods=['POST'])
def checkbox_select():
    global data
    global updatedix
    data_check = request.get_json()
    row_id = data_check.get('rowId')
    checked = data_check.get('checked')
    i = data[data["mac"] == row_id].index
    # if (data.loc[i, "select"].values[0] == 1 and not checked) or (data.loc[i, "select"].values[0] == 0 and checked):
    data.loc[i, "select"] = 1 if checked else 0
    data_update.loc[i, "select"] = 1 if checked else 0
    if checked:
        if len(updatedix) == 0:
            updatedix = list(i.values)
        else:
            updatedix.extend(list(i.values))
    else:
        updatedix=[x for x in [i if x!=i.values[0] else "" for x in updatedix] if x!=""]

    print(f"Row {row_id} checkbox is {'checked' if checked else 'unchecked'}")
    return jsonify(success=True)

@app.route('/checkbox_read_nfc', methods=['POST'])
def checkbox_read_nfc():
    global data
    global reloadpage
    global updatedix
    data_check = request.get_json()
    row_id = data_check.get('rowId')
    checked = data_check.get('checked')
    i = data[data["mac"] == row_id].index
    # if (data.loc[i, "read_nfc"].values[0] == 1 and not checked ) or (data.loc[i, "read_nfc"].values[0] == 0 and checked ):
    data.loc[i, "read_nfc"] = 1 if checked else 0
    data_update.loc[i, "read_nfc"] = 1 if checked else 0
    #data.loc[i, "status"] = "changed"
    if checked:
        if len(updatedix) == 0:
            updatedix = list(i.values)
        else:
            updatedix.extend(list(i.values))
    else:
        updatedix=[x for x in [i if x!=i.values[0] else "" for x in updatedix] if x!=""]
    #reloadpage = "True"
    print(f"Row {row_id} checkbox is {'checked' if checked else 'unchecked'}")
    return jsonify(success=True)


@app.route('/api/data', methods=['POST'])
def update():
    # data = pd.read_csv("scan.csv")
    global data
    global data_update
    global reloadpage
    # global mac_filter
    #flag=False
    try:
        data_page = request.get_json()
        if 'id' not in data_page:
            abort(400)
        # user = User.query.get(data['id'])

        field=list(data_page.items())[1][0]
        # if field=="select":
        #     if data_page["id"] not in mac_filter:
        #         mac_filter.append(data_page["id"])

        if field in ["certificate_id","expiration_date"]:
            ix = data.index
            flag=True
        else:
            ix = data[data["mac"] == data_page["id"]].index
        for i in ix:
            if data.loc[i,field]!=data_page[field]:
                data.loc[i,field]=data_page[field]
                data_update.loc[i,field]=data_page[field]
                updatedix.append(i)
                data.loc[i, "status"] = "changed"
        # for field in ['name', 'age', 'address', 'phone', 'email']:
        #     if field in data:
        #         setattr(user, field, data[field])
        # db.session.commit()
        #if flag:
        reloadpage = "True"
    except Exception as e:
        print(e)

    return '', 204
    # return render_template("editable_table.html"), 204

# Route for the about page
@app.route('/locationpage')
def locationpage():
    return render_template('tagplotupdate.html')

@app.route('/api/locationdata')
def locationdata():
    # Example data for Plotly graph with markers, labels, and colors
    global data
    global anchors_init
    global scan_angles_raw
    global scan_location

    try:
        size_1m = 150

        anchors_data = pd.DataFrame.from_dict(anchors_init, orient="index").reset_index(names=["anchor_mac"])
        ix = (data["x"].isin(["",np.nan,None])) | (data["y"].isin(["",np.nan,None]))
        data_cpy=data.loc[ix==False]
        x = [float(x) for x in data_cpy["x"].values]
        y = [float(y) for y in data_cpy["y"].values]
        if "tag_id" in list(data_cpy.columns):
            mtext = list(data_cpy["tag_id"].values)
        else:
            mtext = list(data_cpy["mac"].values)
        if scan_location is not None:
            msize=[]
            for mac in mtext:
                if sum(scan_location["tag_mac"] == mac)>0:
                    val=scan_location[scan_location["tag_mac"] == mac]["std"].values[0]
                    if not np.isnan(val) :
                        msize.append(int(size_1m * val))
                    else:
                        msize.append(size_1m)
                else:
                    msize.append(size_1m)
        else:
            msize= [int(size_1m) for x in mtext]
        mcolor = ['red' for x in mtext]
        tpos = ['center' for x in mtext]
        x.extend([0, 0, 10, 10])
        y.extend([0, 10, 0, 10])
        mtext.extend(['1D', 'F2', 'C0', '3D'])
        msize.extend([50, 50, 50, 50])

        if scan_angles_raw is not None:
            anchors=list(scan_angles_raw["anchor_mac"].unique())
            mcolor_anchor=[]
            for sid in mtext[len(mtext)-4:]:
                #print(x)
                if sum(anchors_data["short"] == sid) > 0:
                    mcolor_anchor.append('green' if anchors_data[anchors_data["short"]==sid]["anchor_mac"].values[0] in anchors else "red")
                else:
                    mcolor_anchor.append('red')
            mcolor.extend(mcolor_anchor)
        else:
            mcolor.extend(["black","black","black","black"])
        tpos.extend(['top right', 'bottom right', 'top left', 'bottom left'])
        data_location = {
            'x': x, #[3,2,0,0,10,10],
            'y': y,
            'text':mtext ,  # Labels for markers
            'marker_size':msize ,  # Sizes of markers
            'marker_color':mcolor ,  # Colors of markers
            'textposition': tpos
        }
    except Exception as e:
        print(e)
        data_location = {
            'x': [], #[3,2,0,0,10,10],
            'y': [],
            'text':[] ,  # Labels for markers
            'marker_size':[] ,  # Sizes of markers
            'marker_color':[] ,  # Colors of markers
            'textposition': []
        }
    return jsonify(data_location)

@app.route('/data')
def dataupdate():
    global status
    global operation
    global reloadpage
    """send current content"""
    print("datetime:{0} status:{1} operation:{2} reloadpage:{3}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),status,operation,reloadpage))

    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"#"+status+"#"+operation+"#"+reloadpage


@app.route('/data_statuslog')
def data_statuslog():
    """send current content"""
    global statuslog
    print(str(statuslog))
    return str(statuslog)

@app.route('/databar')
def dataupdate_bar():
    """send current content"""
    global barprogress
    if status == "Disabled":
        if barprogress>500:
            barprogress=0
        else:
            barprogress=barprogress+5
    else:
        barprogress=0
    return str(barprogress)

###------------------------------ TEST
@app.route('/callback')
def callback():
    # Example data to send back to the client
    return jsonify({"message": "Grid.js render complete"})

@app.route('/checkbox_state', methods=['GET'])
def checkbox_state():
    row_id = request.args.get('rowId')

    # Example logic: If rowId is even, return checked; otherwise unchecked
    if int(row_id) % 2 == 0:
        return jsonify(checked=True)
    else:
        return jsonify(checked=False)

###------------------------------ TEST

@app.route('/page_configuration')
def page_configuration():
    global columnIds
    global columnIds_location
    global cloud_csv_row
    global cloud_columnIds
    global localpath
    global page_selected
    global page_datatype_selected

    page_reload = False
    if page_datatype_selected!="page_configuration":
        page_reload=True

    page_datatype_selected="page_configuration"
    columnIds=columnIds_base
    columnIds_location=columnIds_location_base
    cloud_csv_row=cloud_csv_row_base
    cloud_columnIds=cloud_columnIds_base
    localpath=localpath_base
    page_selected="page_configuration"
    sync_init()

    if page_reload:
        readscanfile()

    return render_template("page_configuration.html")



@app.route('/get_current_page')
def get_current_page():
    global page_selected
    return jsonify({"page_url": "/"+page_selected})  # Return the current page path as JSON


@app.route('/page_configuration_detail')
def page_configuration_detail():
    global columnIds
    global columnIds_location
    global cloud_csv_row
    global cloud_columnIds
    global localpath
    global page_selected
    global page_datatype_selected
    page_reload = False
    if page_datatype_selected!="page_configuration_detail":
        page_reload=True

    page_datatype_selected="page_configuration_detail"

    columnIds=columnIds_detail
    columnIds_location=columnIds_location_detail
    cloud_csv_row=cloud_csv_row_detail
    cloud_columnIds=cloud_columnIds_detail
    localpath=localpath_detail
    page_selected="page_configuration_detail"
    sync_init()

    if page_reload:
        readscanfile()
    return render_template("page_configuration_detail.html")

@app.route('/page_configuration_configuration')
def page_configuration_configuration():
    global columnIds
    global columnIds_location
    global cloud_csv_row
    global cloud_columnIds
    global localpath
    global page_selected
    global page_datatype_selected

    page_reload=False
    if page_datatype_selected!="page_configuration_configuration":
        page_reload=True

    page_datatype_selected="page_configuration_configuration"

    columnIds=columnIds_configuration
    columnIds_location=columnIds_location_configuration
    cloud_csv_row=cloud_csv_row_configuration
    cloud_columnIds=cloud_columnIds_configuration
    localpath=localpath_configuration
    page_selected="page_configuration_configuration"
    sync_init()

    if page_reload:
        readscanfile()

    return render_template("page_configuration_configuration.html")


@app.route('/page_data_anchors')
def page_data_anchors():
    # Convert DataFrame to HTML table
    anchors_data = pd.DataFrame.from_dict(anchors_init, orient="index").reset_index(names=["anchor_mac"])
    table_html = anchors_data.to_html(classes='table table-striped', index=False)

    # Render the HTML page with the table
    html_content = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>DataFrame Viewer</title>
        <link href="{{ url_for('static', filename='css/mermaid_min.css') }}" type="text/css" rel="stylesheet" />
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body>

        <div class="container">
            <div >
                <button class="go-back-button" onclick="window.history.back();">Go Back</button>
            </div>
            <h1 class="mt-5">Anchors DataFrame</h1>
            <div class="mt-3">
                {table_html}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/page_data_angles')
def page_data_angles():
    # Convert DataFrame to HTML table
    table_html = scan_angles_raw.to_html(classes='table table-striped', index=False)

    # Render the HTML page with the table
    html_content = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>DataFrame Viewer</title>
        <link href="{{ url_for('static', filename='css/mermaid_min.css') }}" type="text/css" rel="stylesheet" />
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body>
    
        <div class="container">
            <div >
                <button class="go-back-button" onclick="window.history.back();">Go Back</button>
            </div>
            <h1 class="mt-5">Raw Angles DataFrame</h1>
            <div class="mt-3">
                {table_html}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)




@app.route('/page_data_location')
def page_data_location():
    # Convert DataFrame to HTML table
    table_html = scan_location.to_html(classes='table table-striped', index=False)

    # Render the HTML page with the table
    html_content = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>DataFrame Viewer</title>
        <link href="{{ url_for('static', filename='css/mermaid_min.css') }}" type="text/css" rel="stylesheet" />
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body>

        <div class="container">
            <div >
                <button class="go-back-button" onclick="window.history.back();">Go Back</button>
            </div>
            <h1 class="mt-5">Location DataFrame</h1>
            <div class="mt-3">
                {table_html}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/page_data_scan')
def page_data_scan():
    # Convert DataFrame to HTML table
    table_html = data.to_html(classes='table table-striped', index=False)

    # Render the HTML page with the table
    html_content = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>DataFrame Viewer</title>
        <link href="{{ url_for('static', filename='css/mermaid_min.css') }}" type="text/css" rel="stylesheet" />
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body>

        <div class="container">
            <div >
                <button class="go-back-button" onclick="window.history.back();">Go Back</button>
            </div>
            <h1 class="mt-5">Scan DataFrame</h1>
            <div class="mt-3">
                {table_html}
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_content)


@app.route("/api/buttons/new", methods=[ 'POST'])
def buttons_web():
    print(request.method)
    interphase=request.referrer[len(request.host_url):]
    buttons_back(request.method,request.form.get("Scan"),request.form.get('Update'),request.form.get('Location'))
    return redirect(url_for('tag_table'))


@app.route("/api/buttons", methods=[ 'POST'])
def buttons():
    print(request.method)
    interphase = request.referrer[len(request.host_url):]
    buttons_back(request.method,request.form.get("Scan"),request.form.get('Update'),request.form.get('Location') )
    return redirect(url_for(page_selected))

def buttons_back(request_method, request_form_get_scan, request_form_get_update, request_form_get_location):
    global status
    global operation
    global semaphore
    global data
    global mac_filter
    global data_update
    global updatedix
    # global request_forced
    global dfilter_back
    global modalOpen

    modalOpen=True
    semaphore=True
    # print(request.method)
    try:
        mac_filter=[]
        dfilter=[x.replace(":","") for x in list(set(list(data[data["select"]==1]["mac"].values)))]
        if request_method == 'POST':
            # if request.form.get('Scan') == 'Scan':
            if request_form_get_scan == 'Scan':
                # pass
                print("Scan")
                status = "Disabled"
                operation = "Scan"
                mac_filter = dfilter if dfilter_back is None else dfilter_back
                dfilter_back = None
                file_path=localpath+"scan.csv"
                file_path_copy = localpath + "scan_copylastscan.csv"
                if os.path.exists(file_path):
                    try:
                        try:
                            # Copy file and metadata, and overwrite if it already exists
                            shutil.copy(file_path, file_path_copy)
                            print(f"File copied successfully from {file_path} to {file_path_copy}")
                        except Exception as e:
                            print(f"Error occurred: {e}")

                        os.remove(file_path)
                        print(f"File '{file_path}' has been deleted.")
                        # return True
                    except Exception as e:
                        print(f"An error occurred while deleting the file: {e}")
                        # return False
                else:
                    print(f"File '{file_path}' does not exist.")

                updatedix = []
            elif request_form_get_update == 'Update':
                # pass # do something else
                print("Update")
                status = "Disabled"
                operation = "Update"
                file_path=localpath+"scan_update.csv"
                mac_filter = dfilter
                dfilter_back = None
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"File '{file_path}' has been deleted.")
                        # return True
                    except Exception as e:
                        print(f"An error occurred while deleting the file: {e}")
                        # return False
                else:
                    print(f"File '{file_path}' does not exist.")
                # global updatedix
                if len(updatedix)>0:
                    # data.loc[list(set(updatedix)),columnIds[:-2]].to_csv(file_path,index=False)
                    dfilter_back = [x.replace(":", "") for x in
                                    list(set(list(data.loc[list(set(updatedix)), "mac"].values)))]
                    #check updatd conig
                    for x in columnIds:
                        if x not in list(data_update.columns):
                            data_update[x]=None

                    data_update.loc[list(set(updatedix)),columnIds[:-2]].to_csv(file_path,index=False)
                else:
                    print("nothing to update")
                updatedix = []

            # elif request.form.get('Location') == 'Location':
            elif request_form_get_location == 'Location':
                # pass # do something else
                print("Location")
                status = "Disabled"
                operation = "Location"
                file_path=localpath+"scan_location.csv"
                file_path_copy = localpath + "scan_location_copylastlocation.csv"
                mac_filter = dfilter
                if os.path.exists(file_path):
                    try:
                        try:
                            # Copy file and metadata, and overwrite if it already exists
                            shutil.copy(file_path, file_path_copy)
                            print(f"File copied successfully from {file_path} to {file_path_copy}")
                        except Exception as e:
                            print(f"Error occurred: {e}")

                        os.remove(file_path)
                        print(f"File '{file_path}' has been deleted.")
                        # return True
                    except Exception as e:
                        print(f"An error occurred while deleting the file: {e}")
                        # return False
                else:
                    print(f"File '{file_path}' does not exist.")
                updatedix = []
            else:
                pass # unknown
                # return render_template("editable_table.html")
        elif request.method == 'GET':
            # return render_template("index.html")
            print("No Post Back Call")
    except Exception as e:
        print(e)
        print("error at buttons")
    semaphore=False
    # if return_page==page_selected:
    #     return redirect(url_for(page_selected))
    # else:
    #     return redirect(url_for('tag_table')) #rredirect(url_for('page_configuration'))ender_template("editable_table.html")

def sync_init():
    global start_init

    if start_init is None:
        start_init = {localpath: False}

    if localpath in start_init.keys():
        status=start_init[localpath]
    else:
        start_init = {localpath: False}
        status=False

    if not status:
        start_init[localpath]=True
        try:
            file_path=localpath+"scan.csv"
            file_path_copy = localpath + "scan_copylastscan.csv"
            if not os.path.exists(file_path):
                print(f"File '{file_path}' does not exist.")
                try:
                    if os.path.exists(file_path_copy):
                        try:
                            # Copy file and metadata, and overwrite if it already exists
                            shutil.copy(file_path_copy,file_path)
                            print(f"File copied successfully from {file_path_copy} to {file_path}")
                        except Exception as e:
                            print(f"Error occurred: {e}")
                    else:
                        print(f"File '{file_path}' empty.")
                        data = pd.DataFrame(columns=columnIds)
                        cloud = pd.DataFrame(columns=cloud_columnIds)
                        data.to_csv(file_path)
                        data.to_csv(file_path_copy)
                        cloud.to_csv(localpath + "cloud.csv")
                except Exception as e:
                    print(f"An error occurred while creating file: {e}")
                    # return False
            try:
                file_path=localpath + "scan_update.csv"
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"An error occurred while deleting the file: {e}")
                # return False

            try:
                file_path=localpath+"scan_location.csv"
                file_path_copy = localpath + "scan_location_copylastlocation.csv"
                if not os.path.exists(file_path):
                    print(f"File '{file_path}' does not exist.")
                    if os.path.exists(file_path_copy):
                        try:
                            # Copy file and metadata, and overwrite if it already exists
                            shutil.copy(file_path_copy,file_path)
                            print(f"File copied successfully from {file_path_copy} to {file_path}")
                        except Exception as e:
                            print(f"Error occurred: {e}")
                    else:
                        print(f"File '{file_path}' empty.")
                        data = pd.DataFrame(columns=location_cvs_columnIds)
                        data.to_csv(file_path)
                        data.to_csv(file_path_copy)
            except Exception as e:
                print(f"An error occurred while creating the file: {e}")
                # return False

        except Exception as e:
            print(e)
            print("error at buttons")


@app.route('/page_scan_parameters')
def page_scan_parameters():
    return render_template('page_scan_parameters.html.j2')
    # return render_template('page_scan_parameters.html')

# New endpoint to provide initial configuration values
@app.route('/get_initial_config', methods=['GET'])
def get_initial_config():
    # Mocked initial values for demonstration
    global scan_parameters

    initial_values = {
        "keep_data": scan_parameters["keep_data"],
        "scan_new_tags": scan_parameters["scan_new_tags"],
        "enable_disable_tags": scan_parameters["enable_disable_tags"],
        "maximum_retries": scan_parameters["maximum_retries"],
        "scan_max_scans": scan_parameters["scan_max_scans"],
        "connect_max_retry": scan_parameters["connect_max_retry"],
        "connect_timeout": scan_parameters["connect_timeout"],
        "max_BoldTags": scan_parameters["max_BoldTags"]
    }
    return jsonify(initial_values)


@app.route('/save_config', methods=['POST'])
def save_config():
    global scan_parameters
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    else:
        scan_parameters = data
    # Process data here (print for demonstration)
    print("Received data:", data)

    # Send a success response
    return jsonify({"status": "success", "message": "Configuration saved"}), 200

@app.route('/spontaneous_list', methods=['POST'])
def receive_list():
    # Get JSON data from the request
    data = request.get_json()

    # Check if data is a list
    if isinstance(data, list):
        # Process the list (e.g., print or perform operations)
        print("Received list:", data)
        # Return a success response
        return jsonify({"status": "success", "message": "List received"}), 200
    else:
        # Return an error if the data is not a list
        return jsonify({"status": "error", "message": "Expected a list in JSON format"}), 400

@app.route("/api/get_scan_data")
def get_scan_data():
    global data
    json_data = data.to_json(orient="records")
    return Response(json_data, mimetype='application/json')

IMAGE_PATH = os.path.join(os.getcwd(), 'static/images', 'rodpump.jpg')
@app.route('/download-image')
def download_image():
    try:
        # send_file sends the file to the user for download
        return send_file(IMAGE_PATH, as_attachment=True, download_name='rodpump.jpg')
    except Exception as e:
        return str(e)


@app.route('/get_backend_status', methods=['GET'])
def get_variables():
    global status
    global operation

    # Return the variables as a JSON response
    return jsonify(status=status, operation=operation)


def run_flask_app():
    global app_host
    global app_port
    if app_host is None:
        app.run(port=app_port, threaded=True)
    else:
        app.run(host=app_host, port=app_port, threaded=True)

def checkstatus():
    global status
    global operation
    global localpath
    global reloadpage
    global last_update_ok
    global data
    global mac_filter
    global data_update
    global read_nfc_done
    global updatedix


    no_update = False
    scan_ready = False
    location_ready = False
    last_update_ok = False
    try:
        file_path = localpath + "scan_update.csv"
        if not os.path.exists(file_path):
            no_update = True
        file_path = localpath + "scan_update_error.csv"
        if not os.path.exists(file_path):
            last_update_ok = True
        file_path = localpath + "scan.csv"
        if os.path.exists(file_path):
            scan_ready = True
        file_path = localpath + "scan_location.csv"
        if os.path.exists(file_path):
            location_ready = True
        print("semaphore {}".format(semaphore))
        if scan_ready and no_update and location_ready:
            if not semaphore and status == "Disabled":
                status = "Enabled"
                if operation=="Scan":
                    # data = pd.read_csv(localpath + "scan.csv")
                    readscanfile()
                    reloadpage="True"
                elif operation=="Update":
                    if os.path.exists(localpath + "scan_update_read.csv"):
                        dfupdate_read = pd.read_csv(localpath + "scan_update_read.csv")
                        for ix in dfupdate_read.index:
                            for k in list(dfupdate_read.columns):
                                if not dfupdate_read[dfupdate_read.index==ix][k].isna().values[0]:
                                    data.loc[data[data['mac']==dfupdate_read.loc[ix,'mac']].index,k]=dfupdate_read.loc[ix,k]
                    data["read_nfc"] = 0  #clear flag
                    data_update = data.copy()
                    for k in list(data_update.columns)[1:]:
                        data_update[k] = None


                    if read_nfc_done:
                    #check if necessary an Scan becuase it was a read_bfc
                        buttons_back("POST", "Scan", "", "")
                        read_nfc_done=False
                    else:
                        reloadpage = "True"

                elif operation == "Location":
                    readscanfile()
                    reloadpage = "True"

                updatedix = []
        else:
            if not scan_ready:
                if not semaphore and status == "Enabled":
                    status = "Disabled"
                    operation = "Scan"
            else:
                if not no_update:
                    if not semaphore and status == "Enabled":
                        status = "Disabled"
                        operation = "Update"
                else:
                    if not location_ready:
                        if not semaphore and status == "Enabled":
                            status = "Disabled"
                            operation = "Location"
    except Exception as e:
        print(e)

def print_statuslog(value, clear=False, addLFCR=True, addtime=False, maxlines=400):
    global statuslog
    global statuslog_maxlines
    if statuslog_maxlines>maxlines:
        statuslog_maxlines=0
        statuslog=""

    statuslog_maxlines=statuslog_maxlines+1

    dtime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if clear:
        if addtime:
            statuslog = dtime + "-> " + value
        else:
            statuslog = value
    else:
        if addLFCR:
            if addtime:
                statuslog=dtime + "-> " + value+"\n"+statuslog
            else:
                statuslog = value + "\n" + statuslog
        else:
            if addtime:
                statuslog = dtime + "-> " + value+statuslog
            else:
                statuslog = value + statuslog

def run_wepapp():
    print("Flask app is running in a separate thread")
    while True:
        time.sleep(1)
        checkstatus()

def set_rssi_tag_scan(set_rssi_tag_scan,init_loading=False):
    global rssi_tag_scan
    global status

    rssi_tag_scan=set_rssi_tag_scan
    if init_loading:
        status = "Enabled"
        readscanfile(True)

def readscanfile(load_init=False ):
    global localpath
    global data
    global data_update
    global scan_angles_raw
    global scan_location
    global rssi_tag_scan

    if os.path.exists(localpath+"scan.csv"):
        data = pd.read_csv(localpath+"scan.csv")
        for x in columnIds:
            if x not in list(data.columns):
                data[x]=None
        if load_init and len(rssi_tag_scan.keys())>0:
            data["status"]="Unkown"
            if rssi_tag_scan is not None:
                try:
                    for ix,rec in data.iterrows():
                        mac=rec["mac"]
                        if mac is not None:
                            mac=mac.replace(":","")
                            if rssi_tag_scan is not None:
                                if mac in list(rssi_tag_scan.keys()):
                                    if "ble_data_crc" in list(data.columns):
                                        if mac in list(rssi_tag_scan.keys()):
                                            if rec["ble_data_crc"]==rssi_tag_scan[mac]["ble_data_crc"]:
                                                data.loc[ix, "status"]="read"

                except Exception as e:
                    print(e)
            data.to_csv(localpath + "scan.csv")

        data_update=data.copy()
        for k in list(data_update.columns)[1:]:
            data_update[k]=None
    else:
        data = pd.DataFrame(columns=columnIds)
        data_update = data.copy()
    if os.path.exists(localpath+"cloud.csv"):
        cloud = pd.read_csv(localpath+"cloud.csv")
    else:
        cloud = pd.DataFrame(columns=cloud_columnIds)

    try:
        data = pd.merge(data, cloud, on='mac', how="left")
        data = data.loc[data["mac"].isna()==False]
    except Exception as e:
        print('--------------ERROR----------------', e)
    
    data=data.fillna("")
    if os.path.exists(localpath + "scan_angles_raw.csv"):
        scan_angles_raw = pd.read_csv(localpath + "scan_angles_raw.csv")
    if os.path.exists(localpath + "scan_location.csv"):
        scan_location = pd.read_csv(localpath + "scan_location.csv")

    if data is not None:
        data["select"]=0
        # data['x'] = data['x'].apply(lambda x: '{:,.1f}'.format(x))
        # data['y'] = data['y'].apply(lambda x: '{:,.1f}'.format(x))

global status
global operation
global localpath
global reloadpage
global statuslog
global last_update_ok
global statuslog_maxlines
global mac_filter
global webcancel
global anchors_init
global read_nfc_done
global dfilter_back
global modalOpen

read_nfc_done=False
global admin_username
global admin_password
global user_role
# start_back=-1
# length_back=-1
app_host="0.0.0.0" #"192.168.1.196"
app_port=5000

app_scan_columnIds=None

webcancel=False
anchors_init=None
data = None
cloud = None
scan_angles_raw = None
scan_location=None
data_update=None
reloadpage="False"
last_update_ok=False
statuslog=""
mac_filter=[]
statuslog_maxlines=0
barprogress = 0
updatedix=[]
semaphore=False
dfilter_back=None
status="Strting"
operation="None"
rssi_tag_scan=None
start_init=None

#localpath="/Users/iansear/Documents/Timbergrove/BoldForge/tgspoc/"
#localpath="c:\\tgspoc\\"

page_selected="page_configuration"
page_datatype_selected=""

#initialized by poc_server.py with global directory
localpath=""    #initialized by poc_server.py with global directory
columnIds=[] #None #['mac', 'name', 'tag_id', 'asset_id', 'certificate_id', 'type', 'expiration_date', 'color', 'series','asset_images_file_extension','read_nfc',  'x', 'y']; Must be initialized by poc_server
cloud_columnIds=None
cloud_csv_row=None
columnIds_location = ['tag_mac', 'out_prob']

localpath_base=""    #initialized by poc_server.py with global directory
columnIds_base = None #['mac', 'name', 'tag_id', 'asset_id', 'certificate_id', 'type', 'expiration_date', 'color', 'series','asset_images_file_extension','read_nfc',  'x', 'y']; Must be initialized by poc_server
cloud_columnIds_base=None
cloud_csv_row_base=None
columnIds_location_base = ['tag_mac', 'out_prob']

localpath_detail=""    #initialized by poc_server.py with global directory
columnIds_detail = None #['mac', 'name', 'tag_id', 'asset_id', 'certificate_id', 'type', 'expiration_date', 'color', 'series','asset_images_file_extension','read_nfc',  'x', 'y']; Must be initialized by poc_server
cloud_columnIds_detail=None
cloud_csv_row_detail=None
columnIds_location_detail = ['tag_mac', 'out_prob']

localpath_configuration=""    #initialized by poc_server.py with global directory
columnIds_configuration = None #['mac', 'name', 'tag_id', 'asset_id', 'certificate_id', 'type', 'expiration_date', 'color', 'series','asset_images_file_extension','read_nfc',  'x', 'y']; Must be initialized by poc_server
cloud_columnIds_configuration=None
cloud_csv_row_configuration=None
columnIds_location_configuration = ['tag_mac', 'out_prob']

location_cvs_columnIds=None
location_cvs_row=None

scan_parameters=scan_parameters={'enable_disable_tags': "none", 'keep_data': True, 'maximum_retries': 3, 'scan_new_tags': True,"scan_max_retry" :1, "scan_max_scans" : 3, "connect_max_retry":3,"connect_timeout":15, "max_BoldTags":2}

admin_username='Admin'
admin_password='1234'
user_role=None
isLoggedIn=False

modalOpen=False

if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    logger.info("Staring webapp..")

    #data = pd.read_csv(localpath+"scan.csv")

    #print(data, flush=True)

    readscanfile()
    # app.run()

    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Main thread can do other tasks here
    # For example, print a message or perform other operations
    while True:
        print("Flask app is running in a separate thread")
        time.sleep(1)
        checkstatus()
