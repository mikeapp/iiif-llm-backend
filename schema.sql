
CREATE TABLE users (
                       username        text PRIMARY KEY NOT NULL,
                       email_address   text not null,
                       created_on      timestamp default CURRENT_TIMESTAMP not null,
                       last_login      timestamp default CURRENT_TIMESTAMP not null,
                       credits         int
);

CREATE TABLE activities (
                            activity_id     SERIAL PRIMARY KEY,
                            username        text NOT NULL,
                            object_id       text,
                            service_provider text,
                            credits_used    int,
                            created_on      timestamp default CURRENT_TIMESTAMP not null,
                            CONSTRAINT fk_username FOREIGN KEY(username) REFERENCES users(username)
);

CREATE VIEW user_credits_used AS SELECT u.username, SUM (a.credits_used) as credits_used FROM users u, activities a WHERE u.username = a.username GROUP BY u.username;

CREATE TABLE ocr (
                     image_id        text NOT NULL,
                     object_id       text NOT NULL,
                     text_engine     text NOT NULL,
                     text_content    text,
                     created_on      timestamp default CURRENT_TIMESTAMP not null,
                     PRIMARY KEY (image_id, object_id, text_engine)
);

CREATE TABLE generic_prompts (
                                 prompt_key      text PRIMARY KEY NOT NULL,
                                 prompt_label    text NOT NULL,
                                 prompt_description  text NOT NULL,
                                 prompt_text     text NOT NULL,
                                 created_on      timestamp default CURRENT_TIMESTAMP not null
);

CREATE TABLE prompts (
                         prompt_key      text PRIMARY KEY NOT NULL,
                         generic_key     text NOT NULL,
                         model           text NOT NULL,
                         prompt_label    text NOT NULL,
                         prompt_description  text NOT NULL,
                         prompt_text     text NOT NULL,
                         created_on      timestamp default CURRENT_TIMESTAMP not null,
                         CONSTRAINT generic_key_fk FOREIGN KEY(generic_key) REFERENCES generic_prompts(prompt_key)
);

CREATE INDEX prompt_key_model_idx ON prompts (prompt_key, model);

GRANT ALL ON users TO aiuser;
GRANT ALL ON activities TO aiuser;
GRANT ALL ON ocr TO aiuser;
GRANT ALL ON generic_prompts TO aiuser;
GRANT ALL ON prompts  TO aiuser;
GRANT SELECT ON user_credits_used TO aiuser;