# Team Gemsbok Small Group project

## Team members
The members of the team are:
- Pradeep Shah
- Kesiena Eforhare
- Yuchen Wang
- Hind Alhokair
- Yusuf Yacoobali

## Project structure
The project is called `system`.  It currently consists of a single app `clubs`.

## Deployed version of the application
The deployed version of the application can be found at [https://fast-taiga-33467.herokuapp.com/](https://fast-taiga-33467.herokuapp.com/).

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`

Clucker project

Home Page Chess Image: [https://unsplash.com/photos/Iq9SaJezkOE](URL)

## Functionality

- Users (except the owner) can choose to leave the club by going to the profile view and then clicking the Quit Club button.
- Owners can delete users by navigating to the user list, clicking on a user and then clicking the Remove User button.
- Owners can reinstate deleted users by clicking on the Removed Members tab on the user list and then clicking on the Reinstate button.
- Both officers and owners can accept/reject applicants by clicking on the Applicants tab on the user list and then clicking on the Accept/Reject button next to the applicant they wish to accept.
- Only owners can promote members to officers by navigating to the user list and then clicking on the Promote button next to the member they wish to promote to officer.
- Only owners can demote officers to members by navigating to the user list and then clicking on the Demote button next to the officer they wish to demote to member.
- Officers cannot see the personal statements and chess level of fellow officers.
