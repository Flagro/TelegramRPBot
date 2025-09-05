// Read values from environment variables passed to the container
const { DB_NAME = "botdb", DB_USER = "botuser", DB_PASSWORD = "change_me" } = process.env;

const dbh = db.getSiblingDB(DB_NAME);
const existing = dbh.getUser(DB_USER);

if (!existing) {
  dbh.createUser({
    user: DB_USER,
    pwd:  DB_PASSWORD,
    roles: [ { role: "readWrite", db: DB_NAME } ]
  });
  print(`Created user ${DB_USER} on db ${DB_NAME}`);
} else {
  // Uncomment to rotate password on redeploys:
  // dbh.updateUser(APP_USER, { pwd: APP_PASS });
  print(`User ${DB_USER} already exists on db ${DB_NAME}`);
}
