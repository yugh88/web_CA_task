from flask import Flask, request, render_template, send_file
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if request.method == 'POST':
        group_file = request.files['group_info']
        hostel_file = request.files['hostel_info']

        # Load data
        group_df = pd.read_csv(group_file)
        hostel_df = pd.read_csv(hostel_file)

        # Strip any leading/trailing whitespace from column names
        group_df.columns = group_df.columns.str.strip()
        hostel_df.columns = hostel_df.columns.str.strip()

        # Debug prints
        print("Group DataFrame Columns:", group_df.columns)
        print("Hostel DataFrame Columns:", hostel_df.columns)

        # Check if 'Members' column exists
        if 'Members' not in group_df.columns:
            return "Error: 'Members' column not found in group information file.", 400

        allocation_result = allocate_rooms(group_df, hostel_df)
        allocation_result.to_csv('allocation_result.csv', index=False)

        return render_template('result.html', tables=[allocation_result.to_html()])


def allocate_rooms(group_df, hostel_df):
    allocation_result = []
    hostel_df['RemainingCapacity'] = hostel_df['Capacity']

    for _, group in group_df.iterrows():
        group_size = group['Members']
        group_gender = group['Gender']
        group_id = group['GroupID']

        suitable_rooms = hostel_df[(hostel_df['Gender'] == group_gender) & (hostel_df['RemainingCapacity'] >= group_size)]
        if not suitable_rooms.empty:
            chosen_room = suitable_rooms.iloc[0]
            allocation_result.append({
                'GroupID': group_id,
                'HostelName': chosen_room['HostelName'],
                'RoomNumber': chosen_room['RoomNumber'],
                'MembersAllocated': group_size
            })
            hostel_df.loc[hostel_df.index == chosen_room.name, 'RemainingCapacity'] -= group_size

    return pd.DataFrame(allocation_result)

@app.route('/download')
def download_file():
    return send_file('allocation_result.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
