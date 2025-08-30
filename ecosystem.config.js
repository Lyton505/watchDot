module.exports = {
    apps: [
        {
                  name: "watchdot",
                  script: "/home/leo44/.pyenv/versions/3.9.11/envs/watchdot-3.9.11/bin/python",
                  args: "main.py",
                  cwd: "/home/leo44/Documents/GitRepos/watchDot",
                  interpreter: "none",
                  cron_restart: "*/5 * * * *",
                  autorestart: false

        }

    ]

}

