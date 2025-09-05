const APP_DB   = _getenv("APP_DB")   || "botdb";
const APP_USER = _getenv("APP_USER") || "botuser";
const APP_PASS = _getenv("APP_PASS") || "change_me";

const dbh = db.getSiblingDB(APP_DB);
const existing = dbh.getUser(APP_USER);

if (!existing) {
  dbh.createUser({
    user: APP_USER,
    pwd:  APP_PASS,
    roles: [ { role: "readWrite", db: APP_DB } ]
  });
} else {
  // Optional: rotate password automatically if APP_PASS changes
  // dbh.updateUser(APP_USER, { pwd: APP_PASS });
}
