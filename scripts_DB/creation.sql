DROP DATABASE IF EXISTS pizzeria;

CREATE DATABASE IF NOT EXISTS pizzeria;

USE pizzeria;

CREATE TABLE IF NOT EXISTS garnitures (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS croutes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS sauces (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS pizzas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    croute_id INT,
    sauce_id INT,
    FOREIGN KEY (croute_id) REFERENCES croutes (id),
    FOREIGN KEY (sauce_id) REFERENCES sauces (id)
);

CREATE TABLE IF NOT EXISTS pizzas_garnitures (
    pizza_id INT,
    garniture_id INT,
    PRIMARY KEY(pizza_id),
    PRIMARY KEY(garniture_id),
    FOREIGN KEY (pizza_id) REFERENCES pizzas (id),
    FOREIGN KEY (garniture_id) REFERENCES garnitures (id)
);

CREATE TABLE IF NOT EXISTS commandes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    temps_commande DATETIME,
    nom_client VARCHAR(255),
    telephone_client VARCHAR(20),
    adresse VARCHAR(255),
    pizza_id INT,
    FOREIGN KEY (pizza_id) REFERENCES pizzas (id)
);

CREATE TABLE IF NOT EXISTS commandes_en_attente (
    commande_id INT PRIMARY KEY,
    FOREIGN KEY (commande_id) REFERENCES commandes (id)
);

DELIMITER $$

CREATE TRIGGER IF NOT EXISTS creation_commande
    AFTER INSERT
    ON commandes FOR EACH ROW
    BEGIN
        INSERT INTO commandes_en_attente (commande_id) VALUES(NEW.id);
    END $$

DELIMITER ;
