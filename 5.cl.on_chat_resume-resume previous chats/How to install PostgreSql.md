# Update packages
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# PostgreSQL will start automatically every time your system boots
sudo systemctl enable postgresql

# Test
psql --version

sudo systemctl status postgresql


Should say active (exited) or active (running).
# If it’s not active, try:

sudo systemctl start postgresql
---------------------------------------------------------------


# Switch to postgres user
sudo -i -u postgres

# Enter PostgreSQL shell
psql

# Create user "admin" with password "admin"
CREATE USER admin WITH PASSWORD 'admin';

#Create database "my_chainlit_db" owned by admin

CREATE DATABASE my_chainlit_db OWNER admin;

# Give privileges
GRANT ALL PRIVILEGES ON DATABASE my_chainlit_db TO admin;

# Exit
\q
exit

# Test
psql -U admin -d my_chainlit_db -h localhost -W

\conninfo
---------------------------------------

