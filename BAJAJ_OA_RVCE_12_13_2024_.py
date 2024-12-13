import json
import pandas as pd
from datetime import datetime
from collections import Counter
from scipy.stats import pearsonr

with open('C:/Users/faiz/Downloads/DataEngineeringQ2.json') as f:
    dataset = json.load(f)

data_list = []
for entry in dataset:
    patient_info = entry['patientDetails']
    consultation_info = entry['consultationData']
    medications = consultation_info['medicines']
    for med in medications:
        patient_data = {
            'id': patient_info.get('_id', ''),
            'fname': patient_info.get('firstName', ''),
            'lname': patient_info.get('lastName', ''),
            'email': patient_info.get('emailId', ''),
            'sex': patient_info.get('gender', ''),
            'dob': patient_info.get('birthDate', ''),
            'phone': entry.get('phoneNumber', '')
        }
        med_data = {
            'med_id': med.get('medicineId', ''),
            'med_name': med.get('medicineName', ''),
            'freq': med.get('frequency', ''),
            'dur': med.get('duration', ''),
            'dur_unit': med.get('durationIn', ''),
            'instr': med.get('instruction', ''),
            'active': med.get('isActive', '')
        }
        merged_data = {**patient_data, **med_data}
        data_list.append(merged_data)

df_data = pd.DataFrame(data_list)

df_data['dob'] = pd.to_datetime(df_data['dob'], errors='coerce')

summary = df_data.groupby(['id', 'fname', 'lname']).agg({
    'med_name': lambda x: ', '.join(x),
    'dur': 'sum'
}).reset_index()

missing_vals = df_data.isnull().sum()
unique_ids = df_data['id'].nunique() == len(df_data['id'])

common_drugs = df_data['med_name'].value_counts().head(10)
top_prescriptions = df_data.groupby('id').size().sort_values(ascending=False).head(10)

print("Missing Values:\n", missing_vals)
print("\nUnique Patient IDs:", unique_ids)
print("\nMost Common Medications:\n", common_drugs)
print("\nPatients with Most Medications:\n", top_prescriptions)
print("\nMedication Summary:\n", summary.head())

details = [entry['patientDetails'] for entry in dataset]
df_details = pd.DataFrame(details)

def missing_percent(col):
    total = len(col)
    missing = col.apply(lambda x: x == '' or pd.isna(x)).sum()
    return round((missing / total) * 100, 2)

first_name_missing = missing_percent(df_details['firstName'])
last_name_missing = missing_percent(df_details['lastName'])
birth_date_missing = missing_percent(df_details['birthDate'])

print(f"{first_name_missing}, {last_name_missing}, {birth_date_missing}")

gender_mode = df_details['gender'].mode()[0]
df_details['gender'].fillna(gender_mode, inplace=True)
df_details['gender'].replace('', gender_mode, inplace=True)

total_count = len(df_details)
female_count = (df_details['gender'] == 'F').sum()
female_pct = round((female_count / total_count) * 100, 2)

print(female_pct)

df_details['birthDate'] = pd.to_datetime(df_details['birthDate'], errors='coerce')
current_year = datetime.now().year
df_details['age'] = current_year - df_details['birthDate'].dt.year

def age_category(age):
    if pd.isna(age):
        return 'Unknown'
    elif age <= 12:
        return 'Child'
    elif 13 <= age <= 19:
        return 'Teen'
    elif 20 <= age <= 59:
        return 'Adult'
    else:
        return 'Senior'

df_details['age_group'] = df_details['age'].apply(age_category)
adult_count = df_details[df_details['age_group'] == 'Adult'].shape[0]

print(adult_count)

med_count_list = []
for entry in dataset:
    consult_info = entry['consultationData']
    meds = consult_info['medicines']
    med_count_list.append(len(meds))

avg_meds = round(sum(med_count_list) / len(med_count_list), 2)

print(avg_meds)

med_names = []
for entry in dataset:
    consult_info = entry['consultationData']
    meds = consult_info['medicines']
    for med in meds:
        med_names.append(med['medicineName'])

med_freq = Counter(med_names)
third_med = med_freq.most_common()[2][0]

print(third_med)

active_count = 0
inactive_count = 0

for entry in dataset:
    consult_info = entry['consultationData']
    meds = consult_info['medicines']
    for med in meds:
        if med['isActive']:
            active_count += 1
        else:
            inactive_count += 1

total_meds = active_count + inactive_count
active_pct = round((active_count / total_meds) * 100, 2)
inactive_pct = round((inactive_count / total_meds) * 100, 2)

print(f"{active_pct}, {inactive_pct}")

phone_data = [entry.get('phoneNumber', '') for entry in dataset]
df_details['phone'] = phone_data

def valid_number(num):
    num = num.replace(' ', '').replace('-', '')
    if num.startswith('+91'):
        num = num[3:]
    elif num.startswith('91'):
        num = num[2:]
    if num.isdigit() and len(num) == 10:
        num_int = int(num)
        return 6000000000 <= num_int <= 9999999999
    return False

df_details['valid_phone'] = df_details['phone'].apply(valid_number)
valid_count = df_details['valid_phone'].sum()

print(valid_count)

patient_records = []
for entry in dataset:
    patient = entry['patientDetails']
    consultation = entry['consultationData']
    med_count = len(consultation['medicines'])
    dob = patient.get('birthDate', None)
    if dob:
        dob = pd.to_datetime(dob, errors='coerce')
        age = datetime.now().year - dob.year
    else:
        age = None
    patient_records.append({
        'pid': patient.get('_id', ''),
        'age': age,
        'med_count': med_count
    })

df_patients = pd.DataFrame(patient_records)
df_patients = df_patients.dropna(subset=['age'])

correlation, _ = pearsonr(df_patients['age'], df_patients['med_count'])
correlation_rounded = round(correlation, 2)

print(correlation_rounded)
