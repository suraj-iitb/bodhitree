**BodhiTree** is an online learning platform developed at IIT Bombay with the mission of providing accessible quality technical education for all, through personalized, flexible, and hands-on complete learning.

# Commands for local setup

## Clone repository
```bash
https://github.com/suraj-iitb/bodhitree.git
```

## Containers up
```bash
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up -d --build
```

## Attach debugger in VS Code
1. Install **Python & Docker extension by Microsoft** in VS Code
2. Click on green traingle to start the debugger

    ![Debugger Image](.images/debug.png)

2. Access API via http://localhost:8765/accounts in browser


# Commands for deployment

## Clone repository
```bash
https://github.com/suraj-iitb/bodhitree.git
```

## Containers up
```bash
docker swarm init
docker stack deploy -c docker-compose.yml -c docker-compose.prod.yml <INSTANCE_NAME>
```

## Access API
Access API via http://0.0.0.0:8765/accounts in browser
