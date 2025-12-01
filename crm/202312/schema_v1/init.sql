CREATE TABLE IF NOT EXISTS users_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO users_test (username) VALUES ('jenkins_user');
SELECT
    id,
    username,
    created_at
FROM users_test;
