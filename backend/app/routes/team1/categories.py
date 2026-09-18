from flask import Blueprint, jsonify, request

from app.middleware.team1_auth import role_required
from app.services.team1.category_service import (
    create_category,
    get_categories,
    get_category_by_id,
    update_category,
    delete_category
)


categories_bp = Blueprint(
    "team1_categories",
    __name__,
    url_prefix="/api/categories"
)


# View/Search Categories
@categories_bp.route("/", methods=["GET"])
@role_required("Owner", "Manager", "Employee", "Supplier")
def get_category_list():
    search = request.args.get("search")

    categories, error = get_categories(search=search)

    if error:
        return jsonify({"error": error}), 500

    return jsonify({"categories": categories}), 200


# View One Category
@categories_bp.route("/<int:category_id>", methods=["GET"])
@role_required("Owner", "Manager", "Employee", "Supplier")
def get_category(category_id):
    category, error = get_category_by_id(category_id)

    if error:
        if error == "Category not found":
            return jsonify({"error": error}), 404

        return jsonify({"error": error}), 500

    return jsonify({"category": category}), 200


# Create Category
@categories_bp.route("/", methods=["POST"])
@role_required("Owner", "Manager")
def create_new_category():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    category_name = data.get("category_name")
    description = data.get("description")

    if not category_name or not category_name.strip():
        return jsonify({"error": "Category name is required"}), 400

    category_name = category_name.strip()

    category, error = create_category(
        category_name,
        description
    )

    if error:
        if error == "Category already exists":
            return jsonify({"error": error}), 409

        return jsonify({"error": error}), 500

    return jsonify({
        "message": "Category created successfully",
        "category": category
    }), 201


# Update Category
@categories_bp.route("/<int:category_id>", methods=["PUT"])
@role_required("Owner", "Manager")
def update_existing_category(category_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    category_name = data.get("category_name")
    description = data.get("description")

    if not category_name or not category_name.strip():
        return jsonify({"error": "Category name is required"}), 400

    category_name = category_name.strip()

    category, error = update_category(
        category_id,
        category_name,
        description
    )

    if error:
        if error == "Category not found":
            return jsonify({"error": error}), 404

        if error == "Category already exists":
            return jsonify({"error": error}), 409

        return jsonify({"error": error}), 500

    return jsonify({
        "message": "Category updated successfully",
        "category": category
    }), 200


# Delete Category
@categories_bp.route("/<int:category_id>", methods=["DELETE"])
@role_required("Owner", "Manager")
def delete_existing_category(category_id):
    success, error = delete_category(category_id)

    if error:
        if error == "Category not found":
            return jsonify({"error": error}), 404

        if error == "Category cannot be deleted because products are assigned to it":
            return jsonify({"error": error}), 409

        return jsonify({"error": error}), 500

    return jsonify({
        "message": "Category deleted successfully"
    }), 200