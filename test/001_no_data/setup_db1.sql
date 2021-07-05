-- MySQL dump 10.13  Distrib 8.0.23, for Win64 (x86_64)
--
-- Host: localhost    Database: djangoledger
-- ------------------------------------------------------
-- Server version	8.0.23

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ledger_category`
--

DROP TABLE IF EXISTS `ledger_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ledger_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ledger_category_user_id_2bd73e4c_fk_auth_user_id` (`user_id`),
  CONSTRAINT `ledger_category_user_id_2bd73e4c_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ledger_entity`
--

DROP TABLE IF EXISTS `ledger_entity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ledger_entity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `category_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ledger_entity_category_id_8a55fce7_fk_ledger_category_id` (`category_id`),
  KEY `ledger_entity_user_id_1c3fd54f_fk_auth_user_id` (`user_id`),
  CONSTRAINT `ledger_entity_category_id_8a55fce7_fk_ledger_category_id` FOREIGN KEY (`category_id`) REFERENCES `ledger_category` (`id`),
  CONSTRAINT `ledger_entity_user_id_1c3fd54f_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2379 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ledger_banknamelookup`
--

DROP TABLE IF EXISTS `ledger_banknamelookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ledger_banknamelookup` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bankname` varchar(255) NOT NULL,
  `entity_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ledger_banknamelookup_entity_id_b8ccf398_fk_ledger_entity_id` (`entity_id`),
  KEY `ledger_banknamelookup_user_id_ace1b4a1_fk_auth_user_id` (`user_id`),
  CONSTRAINT `ledger_banknamelookup_entity_id_b8ccf398_fk_ledger_entity_id` FOREIGN KEY (`entity_id`) REFERENCES `ledger_entity` (`id`),
  CONSTRAINT `ledger_banknamelookup_user_id_ace1b4a1_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2014 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ledger_ledger`
--

DROP TABLE IF EXISTS `ledger_ledger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ledger_ledger` (
  `id` int NOT NULL AUTO_INCREMENT,
  `checknum` int DEFAULT NULL,
  `comments` varchar(255) DEFAULT NULL,
  `amount` int NOT NULL,
  `status` int NOT NULL,
  `transdate` datetime(6) NOT NULL,
  `fitid` varchar(255) DEFAULT NULL,
  `transdest_id` int NOT NULL,
  `transsource_id` int NOT NULL,
  `user_id` int NOT NULL,
  `bankname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ledger_ledger_transdest_id_6e093f84_fk_ledger_entity_id` (`transdest_id`),
  KEY `ledger_ledger_transsource_id_eaf218b7_fk_ledger_entity_id` (`transsource_id`),
  KEY `ledger_ledger_user_id_20de4c7b_fk_auth_user_id` (`user_id`),
  CONSTRAINT `ledger_ledger_transdest_id_6e093f84_fk_ledger_entity_id` FOREIGN KEY (`transdest_id`) REFERENCES `ledger_entity` (`id`),
  CONSTRAINT `ledger_ledger_transsource_id_eaf218b7_fk_ledger_entity_id` FOREIGN KEY (`transsource_id`) REFERENCES `ledger_entity` (`id`),
  CONSTRAINT `ledger_ledger_user_id_20de4c7b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29570 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ledger_settings`
--

DROP TABLE IF EXISTS `ledger_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ledger_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `home_account_id` int NOT NULL,
  `unknown_account_id` int NOT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ledger_settings_user_id_5a067292_fk_auth_user_id` (`user_id`),
  KEY `ledger_settings_home_account_id_e830e254` (`home_account_id`),
  KEY `ledger_settings_unknown_account_id_909bbb01` (`unknown_account_id`),
  CONSTRAINT `ledger_settings_home_account_id_e830e254_fk_ledger_entity_id` FOREIGN KEY (`home_account_id`) REFERENCES `ledger_entity` (`id`),
  CONSTRAINT `ledger_settings_unknown_account_id_909bbb01_fk_ledger_entity_id` FOREIGN KEY (`unknown_account_id`) REFERENCES `ledger_entity` (`id`),
  CONSTRAINT `ledger_settings_user_id_5a067292_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ledger_transactiontype`
--

DROP TABLE IF EXISTS `ledger_transactiontype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ledger_transactiontype` (
  `id` int NOT NULL AUTO_INCREMENT,
  `description` varchar(63) NOT NULL,
  `unsel_fg_color` varchar(15) NOT NULL,
  `unsel_bg_color` varchar(15) NOT NULL,
  `sel_fg_color` varchar(15) NOT NULL,
  `sel_bg_color` varchar(15) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=139 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-06-24 20:10:11
