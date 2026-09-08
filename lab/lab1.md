Question1:

uv is a very fast Python package and environment manager made by Astral

after uv init a README.md file was created which is used as instructions or knowledge the person who's gonna clone this repo needs to know to be able to understand .

src folder which contains an init file as a start and then the coder can add whatever files he wants.


Question 2:

.dvcignore and .gitignore aren't pushed to github and DVC stande for Data Version Control

DVC lets you track those files without storing the large files directly inside Git. Git stores small .dvc metadata files, while the actual large data can live somewhere elseز

Question 3: 


for --global the credentials are stored in  your global DVC configuration file which links it to your profile ,

for --local it just store the credentials for this specific project 

and there is --system which store them on the machine and is used accross profiles.


Question4:

the folder /data has been added to the .gitignore file

because dvc helps with not storing the full big sized files on github (knowing that git is not good with big files) 

Question 5:

Yes a data.dvc file . This file is a small pointer/metadata file that represents the data folder. It does not contain the dataset itself.

It contains information such as:

md5 / hash → identifies the exact version of the dataset.
size → total size of the tracked data.
nfiles → number of files in the directory.
path: data → tells DVC which folder this metadata represents.



Question 6:

Yes the code is there, but obviously the folder /data is not present and this is the work of dvc (/data is in .gitignore). So the data is not there. And there is the data.dvc file present in the git repo which contains metadata that points to the actual location of the data.( I created s sample_data folder which is a sample of the data folder for connection purposes )

On DagsHub, the DVC-tracked sample data is visible and can be browsed, confirming that the DVC remote is working correctly.

Question 7:

No. The DVC-tracked data folders are not downloaded by git clone. Only the .dvc metadata/pointer files are cloned from Git.

After cloning the Git repository into a new directory, the DVC-tracked data was not present because Git only contains the .dvc metadata files. After installing DVC, configuring access to the DVC remote, and running dvc pull, the tracked dataset was successfully downloaded from DagsHub. This demonstrates that Git versions the code and DVC pointers, while DVC retrieves the actual data from remote storage.





Question 8:

No. After checking out the previous Git commit and running dvc checkout, the processed directories disappear because the older sample_data.dvc points to the previous version of the dataset, before those directories were created.

 After going back before the commit:
 
 PS C:\Users\Admin\OneDrive\Documents\Shit\5th year\ML ops\mlops-lab-1> Get-ChildItem sample_data


    Directory: C:\Users\Admin\OneDrive\Documents\Shit\5th year\ML 
    ops\mlops-lab-1\sample_data


Mode                 LastWriteTime         Length Name            
----                 -------------         ------ ----            
d-----          9/8/2026   6:35 PM                evaluation      
d-----          9/8/2026   6:35 PM                training        
d-----          9/8/2026   6:35 PM                validation      




After getting back to the main branch :


(.venv) PS C:\Users\Admin\OneDrive\Documents\Shit\5th year\ML ops\mlops-lab-1> git checkout main
Previous HEAD position was 8199522 Add Sample dataset with DVC
Switched to branch 'main'
Your branch is up to date with 'origin/main'.
(.venv) PS C:\Users\Admin\OneDrive\Documents\Shit\5th year\ML ops\mlops-lab-1> dvc checkout
Building workspace index              |16.7k [00:00, 28.5kentry/s]
Comparing indexes                     |16.7k [00:00, 57.4kentry/s]
Applying changes                        |12.0 [00:00,   626file/s]
M       sample_data\
(.venv) PS C:\Users\Admin\OneDrive\Documents\Shit\5th year\ML ops\mlops-lab-1> Get-ChildItem sample_data


    Directory: C:\Users\Admin\OneDrive\Documents\Shit\5th year\ML 
    ops\mlops-lab-1\sample_data


Mode                 LastWriteTime         Length Name            
----                 -------------         ------ ----            
d-----          9/8/2026   6:35 PM                evaluation      
d-----          9/8/2026   8:52 PM                food11_processed
d-----          9/8/2026   8:52 PM                food11_processed
                                                  _mini           
d-----          9/8/2026   6:35 PM                training        
d-----          9/8/2026   6:35 PM                validation      

