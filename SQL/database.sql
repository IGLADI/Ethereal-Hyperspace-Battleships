CREATE DATABASE IF NOT EXISTS `etherealhyperspacebattleshipsdb` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `etherealhyperspacebattleshipsdb`;

CREATE TABLE IF NOT EXISTS `building` (
  `building_id` int(11) NOT NULL AUTO_INCREMENT,
  `building_name` varchar(255) NOT NULL,
  `building_cost` int(11) NOT NULL,
  `upgrade_cost` int(11) NOT NULL,
  PRIMARY KEY (`building_id`)
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


