module.exports = {
  apps: [
    {
      name: "watchdot",
      script: "/usr/bin/xvfb-run",
      args: "-a python -u main.py",
      cwd: "/home/leo44/Documents/GitRepos/watchDot",
      interpreter: "none",
      cron_restart: "*/5 * * * *",
      autorestart: false,
    },
  ],
};
