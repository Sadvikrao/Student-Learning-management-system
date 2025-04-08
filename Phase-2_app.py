import streamlit as st
from pymongo import MongoClient
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
from pymongo import MongoClient
import gridfs
import base64
import io
from collections import Counter
from collections import defaultdict
import pandas as pd
import numpy as np

# Simulated user database
client = MongoClient('mongodb+srv://krrish852456:krrish852456@cluster0.99khz.mongodb.net/?retryWrites=true&w=majority&appid=Cluster0')

db = client["slms"]
dba=client['assign']
collection = db["slms"]
collection1 = db["Subjects"]
collection2 = db["Instructor"]
cust = db["Customer Care"]
assign=db["assign"]
sum=db["Summary"]
m=db["modules"]
p=db["payment"]
a=db["Attempt"]
ass=db["Exam"]
ab=db["Attendance"]
ag=db["AgAttendance"]
f=db["Feedback"]
carddata=db["card"]
fs = gridfs.GridFS(db)
fsa = gridfs.GridFS(dba)
# Session state initialization
if "reg_in" not in st.session_state:
    st.session_state["reg_in"] = False
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""
if "messages" not in st.session_state:
        st.session_state.messages = {}  # Store chat history per user
if "admin_joined" not in st.session_state:
        st.session_state.admin_joined = {}
if 'mar' not in st.session_state:
    st.session_state.mar=0
if 'mark' not in st.session_state:
    st.session_state.mark=0
if 'exam' not in st.session_state:
    st.session_state.exam=0

#Logout Function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["userid"] = ""
    st.session_state["role"] = ""
    st.session_state["rerun"] = True
    st.rerun()


#Reg function
def reg():
    'Already have an Account'
    if st.button('Login Page'):
        st.session_state["reg_in"] = False
        st.session_state["rerun"] = True
        st.rerun()
    new_userid = st.text_input("New Userid")
    new_password = st.text_input("New Password", type="password")
    s=st.text_input("Specialization")
    
        
    if st.button("Register"):
        if collection.find_one({"id": new_userid}) is not None:
            st.warning("The UserID already EXIST.")
        else:
            if new_userid and new_password:
                y={"id":new_userid,"pwd":new_password,"role":'Student',"spec":s,"balance":300}
                collection.insert_one(y)
                st.success('Registered Sucessfully')
            else:
                st.warning("Please enter both userid and password.")
            st.session_state["reg_in"] = False
            st.session_state["rerun"] = True
            st.rerun()

def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="600"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    #binary_data = pdf_file.getvalue()
    #pdf_viewer(input=binary_data,width=700)

def retrival(c,i,o):
    module=[]
    pdf_files = list(db.fs.files.find({}, {"metadata": 1}))
    if pdf_files!=[]:
        for file in pdf_files:
            metadata = file.get("metadata", {})
            if metadata['course']==c and metadata['id']==i and metadata['option']==o:
                module.append(metadata['name'])
    n=m.find({'id':i,'option':o},{"name":1})
    if n is not None:
        for f in n:
            module.append(f['name'])
        selected_filename = st.selectbox("Select a PDF to View",module)

    query = {"metadata.name": selected_filename}
    results = list(db.fs.files.find(query, {"metadata": 1}))
    
    if results !=[]:
        st.write(results[0]['metadata']['description'])
        file_id = results[0]['_id']
        
        pdf_data = fs.get(file_id)
        if results[0]['metadata']['filename'].split(".")[1]=='pdf':
            display_pdf(pdf_data.read())
        st.download_button(label="Download PDF", data=pdf_data.read(), file_name=selected_filename)    
    

    n=m.find_one({"name":selected_filename})
    if n is not None:
        st.write(n['description'])
    return(selected_filename)

def retrivala(c,ins):
    module=[]
    pdf_files = list(db.fs.files.find({}, {"metadata": 1}))
    if pdf_files!=[]:
        for file in pdf_files:
            metadata = file.get("metadata", {})
            if metadata['course']==c and metadata['id']==ins and metadata['option']=='Assesment':
                module.append(metadata['name'])
    
    n=m.find({'id':ins,'option':'Assesment'},{"name":1})
    
    if n is not None:
        for f in n:
            module.append(f['name'])
        selected_filename = st.selectbox("Select a PDF to View",module)
        
    if a.find_one({'course':c,'ins':ins,'mod':selected_filename,'id':st.session_state['userid']}) is None:
        
        query = {"metadata.name": selected_filename}
        results = list(db.fs.files.find(query, {"metadata": 1}))
        if results!=[]:
            # Dropdown to select a PDF file
            # Retrieve the PDF file from MongoDB
            file_id = results[0]['_id']
            pdf_data = fs.get(file_id).read()
            if results[0]['filename'].split(".")[1]=='pdf':
                
                #display_pdf(pdf_data.read())
                st.warning("Please don't upload PDF file. The PDF file viwer is not working on Cloud.")
            # Convert to bytes and display
            else:
                st.download_button(label="Download", data=pdf_data, file_name=selected_filename)
            
            if results[0]['choice']=='Descriptive':
                st.write(results[0]['metadata']['description'])
                ans=st.text_area('Enter the Answer')

            if results[0]['choice']=='MCQ':
                np.random.shuffle(results[0]['metadata']['a'])
                ans=st.radio(results[0]['metadata']['description'],[results[0]['metadata']['a']])

            if results[0]['choice']=='More than One Answer MCQ':
                ans=[]
                np.random.shuffle(results[0]['metadata']['a'])
                for i in results[0]['metadata']['a']:
                    ci=st.checkbox(i)
                    if ci==True:
                        ans.append(i)

            if results[0]['choice']=='True or False':
                ans=st.radio(results[0]['metadata']['description'],[True,False])
            
        n=m.find_one({"name":selected_filename})
        if n is not None:
            if n['option']=='Assesment':
                if n['choice']=='Descriptive':
                    st.write(n['description'])
                    ans=st.text_area('Enter the Answer')
                if n['choice']=='MCQ':
                    np.random.shuffle(n['a'])
                    ans=st.radio(n['description'],n['a'])
                if n['choice']=='More than One Answer MCQ':
                    ans=[]
                    np.random.shuffle(n['a'])
                    for i in n['a']:
                        ci=st.checkbox(i)
                        if ci:
                            ans.append(i)
                if n['choice']=='True or False':
                    ans=st.radio(n['description'],['True','False'])

                if st.button('submit'):
                    a.insert_one({'course':c,'ins':ins,'mod':selected_filename,'id':st.session_state['userid']})
                    st.session_state.mark=st.session_state.mark+1

                    if ans==n['ans']:
                        
                        st.session_state.mar=st.session_state.mar+1

                        st.success(f'✅Correct Score:{st.session_state.mar}')
                    else:
                        st.write('Wrong')
                        if st.session_state.mark==len(module):
                            st.title(f'Total Score: {st.session_state.mar}')
                            ma=p.find_one({'course':c,'instructor':ins},{'_id':0,'m':1})
                            marks=st.session_state.mar+ma['m']
                            st.session_state.exam=st.session_state.exam+1
                            ass.insert_one({'Exam':f'Exam{st.session_state.exam}','course':c,'instructor':ins,'Marks':st.session_state.mar})
                            p.update_one({'course':c,'instructor':ins},{'$set':{'m':marks}})
                            st.session_state.mar=0
                            st.session_state.mark=0
    else:
        st.warning('Already Answered')

# Login function
def login():
    st.title("Login Page")
    userid = st.text_input("Userid")
    password = st.text_input("Password", type="password")
    'Create an Account'
    if st.button('Registration form'):
        st.session_state["reg_in"] = True
        st.session_state["rerun"] = True
        st.rerun()

    if st.button("Login"):
            user = collection.find_one({"id": userid})
            if user is not None: 
                if user["pwd"] == password:
                    st.session_state["logged_in"] = True
                    st.session_state["userid"] = userid
                    st.session_state["role"] = user["role"]
                    st.session_state["rerun"] = True
                    st.rerun()  # Refresh to show navigation
                else:
                    st.error("Invalid Password")
            else:
                    st.error("Invalid Userid")

def moduleview():
    st.title("📄 Retrieve and Display PDFs from MongoDB")

    # Fetch all stored PDF files
    pdf_files = list(db.fs.files.find({}, {"filename": 1, "_id": 1}))

    # Dropdown to select a PDF file
    if pdf_files!=[]:
        file_options = {file["filename"]: file["_id"] for file in pdf_files}
        selected_filename = st.selectbox("Select a PDF to View", list(file_options.keys()))

        if st.button("Load PDF"):
            # Retrieve the PDF file from MongoDB
            file_id = file_options[selected_filename]
            pdf_data = fs.get(file_id).read()
            
            # Convert to bytes and display
            st.download_button(label="Download PDF", data=pdf_data, file_name=selected_filename, mime="application/pdf")
            
            st.write("📄 **PDF Preview:**")
            st.pdf(io.BytesIO(pdf_data))
    else:
        st.write("⚠️ No PDFs found in the database.")

def mainc():
    llm=ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"],                            #st.secrets["OPEN_API_KEY"]
                   model_name='gpt-4o',
                   temperature=0.0)
    prompt_template='''If any actionable prompt is given the state yes else give the response.   
    Text:
    {context}'''
    PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context"])
    
    i=0
    if st.session_state['userid'] not in st.session_state['messages']:
        st.session_state['messages'][st.session_state['userid']] = [{"role": "assistant", "content": "Hello! Welcome to customer care. How Can I help you?"}]
        st.session_state.admin_joined[st.session_state['userid']] = False
        i=1    
    if i==1:
        st.session_state["messages"].update([i for i in sum.find({})][0])
        i=0
    else:
        st.session_state["messages"]=[i for i in sum.find({})][0]

    for msg in st.session_state.messages[st.session_state['userid']]:
        
        st.chat_message(msg["role"]).write(msg["content"])
    
    if prompt := st.chat_input():
    
        st.session_state["messages"][st.session_state['userid']].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        chain = LLMChain(llm=llm, prompt=PROMPT)
        answer=chain.run(prompt)
        if re.search(r'\bYes\b', answer):
            cust.insert_one({'id':st.session_state["userid"],'query':prompt})
            st.chat_message("assistant").write("Notified to the Admin, He will get back to you soon...")
            st.session_state.admin_joined[st.session_state['userid']] = True
            
            
        elif not st.session_state.admin_joined[st.session_state['userid']]:
            prompt_template='''Accept the queries as a customer care and give an accuarte reply.   
            Text:
            {context}'''
            PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context"])
            chain = LLMChain(llm=llm, prompt=PROMPT).run(prompt)
            st.session_state["messages"][st.session_state['userid']].append({"role": "assistant", "content": chain})
            st.chat_message("assistant").write(chain)

    i=1
    sum.delete_many({})
    sum.insert_one(st.session_state["messages"])
    

       
# Main app interface Student
def maini():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Module", "view Assignments","Roll Call","View Attendance","Customer Care"])

    if page == "Dashboard":
        st.title("Dashboard")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        documents=collection2.find({"Instructor": {"$in": [st.session_state["userid"]]}},{"course": 1, "_id": 0})
        key_values = [doc['course'] for doc in documents if 'course' in doc]
        optionm = st.selectbox("Course",(key_values))

    elif page == "Module":
        st.title("Module")
        st.write("Welcome to the Module creation page.")
        flag = st.toggle("AI Correction")
        documents=collection2.find({"Instructor": {"$in": [st.session_state["userid"]]}},{"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        optionm = st.selectbox("Course",(key_values))
        name=st.text_input("Enter the module name")
        e=None
        existing_file = db.fs.files.find_one({"metadata.name": name})
        e=m.find_one({"name":name})
        if existing_file is not None or e is not None:
            st.warning("⚠️ A file with this unique ID already exists! Please enter a different ID.")
        else:
            description=st.text_area("Enter the text")
            # File uploader widget
            uploaded_file = st.file_uploader("Upload a PDF file", type=[])
            option = st.selectbox("Module",('Learning Content','Assignment','Assesment'))
            if option=='Learning Content' or option=='Assignment':
                
                if st.button("Upload"):
                    
                    if uploaded_file.name.split('.')[1]=='pdf':
                        st.warning("Please don't upload PDF file. The PDF file viwer is not working on Cloud.")
                    else:
                        if uploaded_file is not None:
                            st.success(f"✅ Uploaded: {uploaded_file.name}")
    
                            # Convert file to binary for MongoDB storage
                            file_data = uploaded_file.read()
                            
                            # Check if file already exists in MongoDB
                            existing_file = db.fs.files.find_one({"filename": uploaded_file.name})
                            
                            if existing_file:
                                st.warning("⚠️ File already exists in MongoDB.")
                            else:
                                # Store file in GridFS
                                if option=='Learning Content':
                                    file_id = fs.put(file_data, filename=uploaded_file.name,metadata={"filename":uploaded_file.name,"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option})
                                    st.success(f"📁 File saved to MongoDB with ID: {file_id}")
                                else:
                                    file_id = fs.put(file_data, filename=uploaded_file.name,metadata={"filename":uploaded_file.name,"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'dead':dt})
                                    st.success(f"📁 File saved to MongoDB with ID: {file_id}")
                    
                        
            if option=='Assesment':
                m.delete_many({option:"Assesment"})
                choice = st.selectbox("Type of Question",('Descriptive','MCQ','More than One Answer MCQ','True or False'))
                if choice=='Descriptive':
                    if st.button("Upload"):
                        if uploaded_file is not None:
                            st.success(f"✅ Uploaded: {uploaded_file.name}")

                            # Convert file to binary for MongoDB storage
                            file_data = uploaded_file.read()
                            
                            # Check if file already exists in MongoDB
                            existing_file = db.fs.files.find_one({"filename": uploaded_file.name})
                            
                            if existing_file:
                                st.warning("⚠️ File already exists in MongoDB.")
                            else:
                                # Store file in GridFS
                                file_id = fs.put(file_data, filename=uploaded_file.name,metadata={"filename":uploaded_file.name,"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice})
                                st.success(f"📁 File saved to MongoDB with ID: {file_id}")

                        else:
                            m.insert_one({"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice})
                            st.success(f"✅ Uploaded")

                if choice=='MCQ' or choice=='More than One Answer MCQ':
                    n1=int(st.text_input("No. of options:",4))
                    a=[]
                    for i in range(n1):
                        x=st.text_input(f"{i}.")
                        a.append(x)
                    if choice=='MCQ':
                        an=st.text_input('Ans:')
                    if choice=='More than One Answer MCQ':
                        an=[]
                        n2=int(st.text_input("No. of answers:",4))
                        for i in range(n2):
                            x1=st.text_input(f"{i}.",key=f'ans{i}')
                            an.append(x1)

                    if st.button("Upload"):
                            if uploaded_file is not None:
                                st.success(f"✅ Uploaded: {uploaded_file.name}")

                                # Convert file to binary for MongoDB storage
                                file_data = uploaded_file.read()
                                
                                # Check if file already exists in MongoDB
                                existing_file = db.fs.files.find_one({"filename": uploaded_file.name})
                                
                                if existing_file:
                                    st.warning("⚠️ File already exists in MongoDB.")
                                else:
                                    # Store file in GridFS
                                    file_id = fs.put(file_data, filename=uploaded_file.name,metadata={"filename":uploaded_file.name,"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice,'a':a,'ans':an})
                                    st.success(f"📁 File saved to MongoDB with ID: {file_id}")

                            else:
                                m.insert_one({"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice,'a':a,'ans':an})
                                st.success(f"✅ Uploaded")
        
                if choice=='True or False':
                    an=st.text_input('Ans:')
                    if st.button("Upload"):
                            if uploaded_file is not None:
                                st.success(f"✅ Uploaded: {uploaded_file.name}")

                                # Convert file to binary for MongoDB storage
                                file_data = uploaded_file.read()
                                
                                # Check if file already exists in MongoDB
                                existing_file = db.fs.files.find_one({"filename": uploaded_file.name})
                                
                                if existing_file:
                                    st.warning("⚠️ File already exists in MongoDB.")
                                else:
                                    # Store file in GridFS
                                    file_id = fs.put(file_data, filename=uploaded_file.name,metadata={"filename":uploaded_file.name,"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice,'ans':an})
                                    st.success(f"📁 File saved to MongoDB with ID: {file_id}")

                            else:
                                m.insert_one({"name": name, "course": optionm, "description": description,'id':st.session_state['userid'],'option':option,'flag':flag,'choice':choice,'ans':an})
                                st.success(f"✅ Uploaded")
    
    elif page == "view Assignments":
        st.title("view Assignments")
        module=[]
        documents=collection2.find({"Instructor": {"$in": [st.session_state["userid"]]}},{"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
            optionm = st.selectbox("Course",(key_values))

        pdf_files = list(db.fs.files.find({}, {"metadata": 1}))
        if pdf_files!=[]:
            for file in pdf_files:
                metadata = file.get("metadata", {})
                if metadata['course']==optionm:
                    module.append(metadata['name'])
        n=m.find({},{"name":1})
        if n is not None:
            for f in n:
                module.append(f['name'])
        selected_filename = st.selectbox("Select module",module)
        pdf_files = dba.fs.files.find({'filename': {"$regex": selected_filename}}, {"filename": 1})
        
        
        a=[]
        if pdf_files is not None:
            for i in pdf_files:
                a.append(i['filename'])    
        selected_filename = st.selectbox("Select a PDF to View",a)
        file_id = dba.fs.files.find_one({"filename":selected_filename}, {"_id": 1})
        
        if file_id is not None:
            pdf_data = fsa.get(file_id['_id']).read()
            if 'pdf' in selected_filename.split('.'):
                display_pdf(pdf_data)
        # Convert to bytes and display
        st.download_button(label="Download PDF", data=pdf_data, file_name=selected_filename)

    elif page == "Roll Call":
        st.title("Roll Call")
        documents=collection2.find({"Instructor": {"$in": [st.session_state["userid"]]}},{"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        optionm = st.selectbox("Course",(key_values))
        ma=p.find({'course':optionm,'instructor':st.session_state['userid']},{'_id':0,'id':1})
        r=[]
        for i in ma:
            id=st.checkbox(i['id'])
            if id==True:
                r.append(i['id'])
        if st.button('Submit'):
            ab.insert_one({'course':optionm,'instructor':st.session_state['userid'],'att':r})
            if ag.find({}) is not None:
                ag.delete_many({})
            data=list(ab.find({},{'_id':0,'att':1}))
            all_att = [course for doc in data for course in doc["att"]]
            att_counts = Counter(all_att)
            att=dict(att_counts)
            att.update({'course':optionm,'instructor':st.session_state['userid']})
            ag.insert_one(att)
    
    elif page=="View Attendance":
        st.title("Attendance")
        documents=collection2.find({"Instructor": {"$in": [st.session_state["userid"]]}},{"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        optionm = st.selectbox("Course",(key_values))
        ma=ag.find({'course':optionm,'instructor':st.session_state['userid']},{'_id':0,'course':0,'instructor':0})
        for i in ma:
            print('i')
            st.write(pd.DataFrame([i]))
            
        
    elif page == "Customer Care":
        st.title("Customer Care")
        mainc()

    if st.button("Logout"):
        logout()

# Main app interface Instructor
def mains():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Module", "Assignment","Assesment","Course Recom","Prof Recom","Payment","Feedback","Customer Care"])
    if page == "Dashboard":
        st.title("Home Page")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        documents = p.find({'id':st.session_state['userid']}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = p.find({'id':st.session_state['userid'],"spec":s}, {"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        c = st.selectbox("course",key_values)
        
    elif page == "Module":
        st.title("Student Dashboard")
        st.write(f"Welcome to the {st.session_state['userid']} page.")
        documents = p.find({'id':st.session_state['userid']}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = p.find({"spec":s,'id':st.session_state['userid']}, {"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        c = st.selectbox("course",key_values)
        ins = p.find_one({"spec":s,'course':c}, {"instructor": 1, "_id": 0})
        if ins is not None:
            i=ins['instructor']
            retrival(c,i,'Learning Content')

    elif page == "Assignment":
        st.title("Student Dashboard")
        st.write("Welcome to the student page.")
        documents = p.find({'id':st.session_state['userid']}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = p.find({"spec":s,'id':st.session_state['userid']}, {"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        c = st.selectbox("course",key_values)
        ins = p.find_one({"spec":s,'course':c}, {"instructor": 1, "_id": 0})
        if ins is not None:
            i=ins['instructor']
            m=retrival(c,i,page)

        uploaded_file = st.file_uploader("Upload a PDF file", type=[])
        if st.button('upload'):
            if uploaded_file is not None:
                file_data = uploaded_file.read()
                display_pdf(file_data)
                file_id = fsa.put(file_data, filename=f'{m}.{i}.{uploaded_file.name}.{st.session_state["userid"]}')
                st.success(f"📁 File saved to MongoDB with ID: {file_id}")

    elif page == "Assesment":
        st.title("Assesment")
        st.write("Welcome to the user page.")
        documents = p.find({'id':st.session_state["userid"]}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = p.find({'id':st.session_state['userid'],"spec":s}, {"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
            if key_values != []:
                c = st.selectbox("course",key_values)
                ins = p.find_one({"id":st.session_state['userid'],"spec":s,'course':c}, {"instructor": 1, "_id": 0})
                if ins is not None:
                    i=ins['instructor']
                    retrivala(c,i)
        
    elif page=="View Attendance":
        st.title("Attendance")
        documents=collection2.find({"Instructor": {"$in": [st.session_state["userid"]]}},{"course": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['course'] for doc in documents if 'course' in doc]
        optionm = st.selectbox("Course",(key_values))
        ma=ag.find({'course':optionm,'instructor':st.session_state['userid']},{'_id':0,'course':0,'instructor':0,f'{st.session_state["userid"]}':1})
        for i in ma:
            print('i')
            st.write(pd.DataFrame([i]))

    elif page == "Payment":
        st.title("Payment")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
            s = st.selectbox("Specialization",(key_values))
        if documents is not None:
            documents = collection1.find({"spec":s}, {"course": 1, "_id": 0})
            key_values = [doc['course'] for doc in documents if 'course' in doc]
            c = st.selectbox("course",key_values[0])

        exist=p.find_one({'course':c,'id':st.session_state['userid']})
        if exist is None:
            documents = collection2.find({"spec":s,"course":c}, {"Instructor": 1, "_id": 0})
           
            key_values = [doc['Instructor'] for doc in documents if 'Instructor' in doc]

            if key_values != []:
                ins = st.selectbox("Instructor",key_values[0])
                card=st.selectbox("Card",['credit','debit'])
                cardno=st.text_input('Enter the Card Number')
                N=st.text_input('Name of the Card Holder')
                exp=st.text_input('Expiry Date')
                sc=st.text_input('Security Number')
                if st.button('pay'):

                    b=carddata.find_one({'CardNo':cardno,'Name':N,'Type':card,'SEC':sc,'Expdate':exp},{"balance":1})
                    
                    if b is not None:
                        if b['balance']>100:
                            i=b['balance']-100
                            carddata.update_one({'CardNo':cardno}, {"$set":{'balance':i}})
                            p.insert_one({"id":st.session_state['userid'],"spec":s,"course":c,"instructor":ins,'m':0})
                            st.success(f"payed successfully, you have {i} balance in your account")
                        else:
                            st.error("No enough balance")
                    else:
                        st.error("Invalid Card Details")
        else:
            st.warning("Already Payed")

    elif page=='Feedback':
        documents = p.find({'id':st.session_state['userid']}, {"spec": 1, "_id": 0})
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
            s = st.selectbox("Specialization",(key_values))
            if documents is not None:
                documents = p.find({'id':st.session_state['userid'],"spec":s}, {"course": 1, "_id": 0})
                key_values = [doc['course'] for doc in documents if 'course' in doc]
                c = st.selectbox("course",key_values)

                documents = p.find({'id':st.session_state['userid'],"course":c,"spec":s}, {"instructor": 1, "_id": 0})
                if documents is not None:
                    key_values = [doc['instructor'] for doc in documents if 'instructor' in doc]
                    if key_values != []:
                        i = st.selectbox("instructor",key_values)

                        documents = p.find({"spec":s,'id':st.session_state['userid'],"course": c})
                        d=[di for di in f.find({"spec":s,'id':st.session_state['userid'],"course": c})]
                        if d == []:
                            if documents is not None:
                                    a1=st.checkbox("Very Interactive")
                                    b1=st.checkbox("Very Strict")
                                    c1=st.checkbox("Can score high")
                                    d1=st.checkbox("Very lineant in Correction")
                                    e1=st.checkbox("adds Grace Marks")
                                    f1=st.checkbox("Can learn a lot")
                            if st.button('submit'):
                                f.insert_one({'id':st.session_state['userid'],'spec':s,'course':c,'instructor':i,'vi':a1,'vs':b1,'cs':c1,'vc':d1,'agm':e1,'cl':f1})
                        else:
                            st.warning('Already Submitted')
            
    elif page == "Course Recom":

        llm=ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"],                            #st.secrets["OPEN_API_KEY"]
                   model_name='gpt-4o',
                   temperature=0.0)
        if "ms" not in st.session_state:
            st.session_state["ms"] = [{"role": "assistant", "content": "Enter your profession to get course recommendations:"}]

        st.title("Course Recommendation System")
        documents=collection1.find({},{'course':1,'_id':0})
        key_values = [i for doc in documents for i in doc['course'] if 'course' in doc]

        prompt_template='''Accept prompt as a course recommender in the form of Profession and suggest four from the courses in {key_values}   
        to be taken to go into the given profession
        Text:
        {context}'''
        PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context","key_values"])

        answer='Enter the profession to take the regarding courses'
        st.session_state.ms.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)
        
        if prompt := st.chat_input():
            st.session_state.ms.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            formatted_prompt={"context":prompt, "key_values":", ".join(key_values)}
            chain = LLMChain(llm=llm, prompt=PROMPT).run(formatted_prompt)
            st.session_state.ms.append({"role": "assistant", "content": chain})
            st.chat_message("assistant").write(chain)
        
    elif page == "Prof Recom":
        st.title("Prof Recommendation System")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        
        if documents is not None:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
            s = st.selectbox("Specialization",(key_values))
            if documents is not None:
                documents = collection1.find({"spec":s}, {"course": 1, "_id": 0})
                key_values = [doc['course'] for doc in documents if 'course' in doc]
                c = st.selectbox("course",key_values[0])
                fe=f.find({'spec':s,'course':c},{'instructor': 1, 'vi': 1, 'vs': 1, 'cs': 1, 'vc': 1, 'agm': 1, 'cl':1,'_id':0})
                
                ab = defaultdict(lambda: defaultdict(int))
                for it in fe:
                    instructor=it['instructor']
                    for key, value in it.items():
                        if key != 'instructor':
                            ab[instructor][key] = 0
                            if value is True:
                                ab[instructor][key] += 1
                pr=pd.DataFrame([{'Instructor':k,'Interactive':v['vi'],'Strict':v['vs'],'high score':v['cs'],'lineant':v['vc'],'grace':v['agm'],'learn':v['cl']} for k, v in ab.items()])
                st.dataframe(pr)

    elif page == "Customer Care":
        st.title("Customer Care")
        mainc() 


    if st.button("Logout"):
        logout()


# Main app interface Admin
def maina():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home Page","Instruct Reg", "Course Reg", "Course View","Course Assign","Assign View","Notification"])
    
    if page == "Home Page":
        st.title("Home Page")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")

    elif page == "Instruct Reg":
        st.title("Instructor Registration")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        new_userid = st.text_input("New Userid")
        new_password = st.text_input("New Password", type="password")
        s=st.text_input("Specialization")
        if st.button("Register"):
            if collection.find_one({"id": new_userid}) is not None:
                st.warning("The UserID already EXIST.")
            else:
                if new_userid and new_password:
                    y={"id":new_userid,"pwd":new_password,"role":'Instructor',"spec":s,"balance":300}
                    collection.insert_one(y)
                    st.success('Registered Sucessfully')
                else:
                    st.warning("Please enter both userid and password.")

    elif page == "Course Reg":
        st.title("Course Registration")
        st.write(f"Hello, {st.session_state['userid']}! You are logged in as {st.session_state['role']}.")
        s=st.text_input("Specialization")
        c=st.text_input("Course")
        exist=list(collection1.find({'spec':s,'course':c}))
        
        if st.button("Insert"):
                if exist ==[]:
                    spec=collection1.find_one({"spec": s})
                    if spec is not None:
                        a=spec['course']
                        a.append(c)
                        collection1.update_one({"spec": s}, {"$set":{'course':a}})
                        st.success(f"Data appended successfully to key: {c}")
                    else:
                        # Create a new document if key does not exist
                            collection1.insert_one({'spec':s,'course':[c]})
                            st.success(f"New key created, data inserted: {s}")
                else:
                        st.warning("The Subject Already Exist")

    elif page == "Course View":
        st.title("Course View")
        st.write("Welcome to the Course View.")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        option = st.selectbox("Specialization",(key_values))
        if option:
        # Find all documents where the key exists
            courses = collection1.find({'spec':option})
            if documents:
                st.write(f"Documents with the key '{option}':")
                st.dataframe(courses)  # Display documents in a table format
            else:
                st.write(f"No documents found with the key: {option}")

    elif page == "Course Assign":
        st.title("Course Registration")
        st.write("Welcome to the Course page.")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        key_values = [doc['spec'] for doc in documents if 'spec' in doc]
        
        s = st.selectbox("Specialization",(key_values))

        documents = collection1.find({"spec":s}, {"course": 1, "_id": 0})
        key_values = [doc['course'] for doc in documents if 'course' in doc]
        c = st.selectbox("course",key_values[0])

        docum = collection.find({"role":"Instructor","spec":s}, {"id": 1, "_id": 0})
        key_values = [doc['id'] for doc in docum if 'id' in doc]
        i = st.selectbox("Instructor",(key_values))

        if st.button("Insert"):
            spec=collection2.find_one({"spec": s,'course':c})
            if  spec is not None:
                # Append new values to the existing array
                a=spec['Instructor']
                a.append(i)
                collection2.update_one({"spec": s,'course':c}, {"$set":{'Instructor':a}})
                st.success(f"Data appended successfully to key: {c}")
            else:
                # Create a new document if key does not exist
                collection2.insert_one({'spec':s,'course':c,'Instructor':[i]})
                st.success(f"New key created, data inserted: {s}")

    elif page == "Assign View":
        st.title("Assign View")
        st.write("Welcome to the Assign View.")
        documents = collection1.find({}, {"spec": 1, "_id": 0})
        if documents!=[]:
            key_values = [doc['spec'] for doc in documents if 'spec' in doc]
            option = st.selectbox("Specialization",(key_values))
        if option:
        # Find all documents where the key exists
            courses = collection2.find({'spec':option})
            if courses:
                st.write(f"Documents with the key '{option}':")
                st.dataframe(courses)  # Display documents in a table format
            else:
                st.write(f"No documents found with the key: {option}")

    elif page == "Notification":
        st.session_state["messages"]=[i for i in sum.find({})][0]
        st.title("Customer Service")
        m=[]
        c=cust.find({},{'query':1,'id':1,'_id':0})
        if c !=[]:
            for j in c:
                    a=f'{j["id"]}.{j["query"]}'
                    m.append(a)
            option = st.selectbox("Notifications",(m))
            
            if option is not None:
                o=option.split('.')
                for msg in st.session_state.messages[o[0]]:
                    st.chat_message(msg["role"]).write(msg["content"])
                if prompt := st.chat_input():
                    st.session_state["messages"][o[0]].append({"role": "admin", "content": prompt})
                    st.chat_message("admin").write(prompt)
                if st.button('clear'):
                    cust.delete_one({'id':o[0],'query':o[1]})
                    st.session_state.admin_joined[st.session_state['userid']]=False
                
                sum.delete_many({})
                sum.insert_one(st.session_state["messages"])
                
    
        else:
            st.write('No Notifications')

        
            
        
    if st.button("Logout"):
        logout()


# Control access
if not st.session_state["reg_in"]:
    if not st.session_state["logged_in"]:
        login()
    else:
        if st.session_state['role']=='Student':
            mains()
        if st.session_state['role']=='Admin':
            maina()
        if st.session_state['role']=='Instructor':
            maini()

else:
    reg()
