from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Column, Table, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="user", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }

    def all_user_favorites(self):
        results = list(map(lambda item: item.serialize(), self.favorites))
        return {
            "id": self.id,
            "email": self.email,
            "favorites": results,
        }


class Favorite(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    character_id: Mapped[int | None] = mapped_column(
        ForeignKey("character.id"), nullable=True)
    planet_id: Mapped[int | None] = mapped_column(
        ForeignKey("planet.id"), nullable=True)
    vehicle_id: Mapped[int | None] = mapped_column(
        ForeignKey("vehicle.id"), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="favorites")
    character: Mapped["Character"] = relationship(
        "Character", back_populates="favorites")
    planet: Mapped["Planet"] = relationship(
        "Planet", back_populates="favorites")
    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle", back_populates="favorites")

    def serialize(self):
        result = {
            "id": self.id
        }

        if self.character_id and self.character:
            result["resource_id"] = self.character_id
            result["type"] = "character"
            result["name"] = self.character.name
            result["gender"] = self.character.gender
            result["height"] = self.character.height
            result["mass"] = self.character.mass

        elif self.planet_id and self.planet:
            result["resource_id"] = self.planet_id
            result["type"] = "planet"
            result["name"] = self.planet.name
            result["terrain"] = self.planet.terrain
            result["climate"] = self.planet.climate
            result["diamater"] = self.planet.diameter

        elif self.vehicle_id and self.vehicle:
            result["resource_id"] = self.vehicle_id
            result["type"] = "vehicle"
            result["name"] = self.vehicle.name
            result["model"] = self.vehicle.model
            result["passengers"] = self.vehicle.passengers
            result["length"] = self.vehicle.length

        return result


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    terrain: Mapped[str] = mapped_column(String(120))
    climate: Mapped[str] = mapped_column(String(120))
    diameter: Mapped[int] = mapped_column(nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="planet")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "terrain": self.terrain,
            "climate": self.climate,
            "diameter": self.diameter,
        }


class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    gender: Mapped[str] = mapped_column(String(120))
    height: Mapped[str] = mapped_column(nullable=False)
    mass: Mapped[str] = mapped_column(nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="character")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "height": self.height,
            "mass": self.mass,
        }


class Vehicle(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    model: Mapped[str] = mapped_column(String(120))
    passengers: Mapped[int] = mapped_column(nullable=False)
    length: Mapped[int] = mapped_column(nullable=False)

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite", back_populates="vehicle")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "passengers": self.passengers,
            "length": self.length,
        }
