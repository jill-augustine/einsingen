from http.cookies import Morsel
import json
from django.http import HttpResponse
import pytest


@pytest.mark.django_db
def test_healthcheck(client):
    response = client.get("/api/health")
    assert response.status_code == 200


def create_test_user(username: str, password: str):
    from django.contrib.auth import get_user_model

    django_user_model = get_user_model()
    test_user = django_user_model.objects.create_user(username=username, password=password)
    return test_user, password


class TestUser:

    @pytest.fixture()
    def user1(self, db):
        return create_test_user("user1", "password1")

    @pytest.fixture()
    def user2(self, db):
        return create_test_user("user2", "password2")

    def test_creation(self, client):
        """Test creation of user via endpoint, not via django user model."""
        some_test_username = "some_test_username"
        resp: HttpResponse = client.post(
            "/api/users", {"username": some_test_username, "password": "password"}, "application/json"
        )
        assert resp.status_code == 201
        assert "sessionid" not in resp.cookies
        resp_body = resp.json()
        assert resp_body.get("username") == some_test_username
        assert resp_body.get("options", {}).get("is_guest") in [None, False]  # Is None if no options set

    def test_creation_existing_username(self, client, user1):
        user1, _ = user1
        resp: HttpResponse = client.post(
            "/api/users", {"username": user1.username, "password": "password"}, "application/json"
        )
        assert resp.status_code == 400
        assert "sessionid" not in resp.cookies
        resp_body = resp.json()
        assert resp_body.get("detail") == "User with that username already exists"

    def test_deletion_as_superuser(self, admin_client, user1, django_user_model):
        # test user deletion (superuser only)
        user1, _ = user1
        del_resp: HttpResponse = admin_client.delete(f"/api/users/{user1.username}")
        assert del_resp.status_code == 200
        del_resp_body = del_resp.json()
        assert del_resp_body.get("username") == user1.username
        assert not del_resp_body.get("options")  # empty dict of missing or otherwise falsy
        assert not django_user_model.objects.filter(username=user1.username).exists()

    def test_deletion_as_own_user(self, client, user1, django_user_model):
        # test deletion of own user
        user1, password = user1
        client.login(username=user1.username, password=password)
        del_resp: HttpResponse = client.delete(f"/api/users/{user1.username}")
        assert del_resp.status_code == 200
        del_resp_body = del_resp.json()
        assert del_resp_body.get("username") == user1.username
        assert not del_resp_body.get("options")  # empty dict of missing or otherwise falsy
        assert not django_user_model.objects.filter(username=user1.username).exists()

    def test_deletion_as_other_user(self, client, user1, user2):
        # test user deletion (regular user to fail)
        user1, password1 = user1
        user2, password2 = user2
        client.login(username=user1.username, password=password1)
        del_resp: HttpResponse = client.delete(f"/api/users/{user2.username}")
        assert del_resp.status_code == 403
        del_resp_body = del_resp.json()
        assert del_resp_body.get("detail") == "You do not have permission to delete this user"

    def test_deletion_nonexistent_user(self, admin_client):
        # test user deletion non-existent user
        del_resp: HttpResponse = admin_client.delete(f"/api/users/someusername")
        assert del_resp.status_code == 404
        del_resp_body = del_resp.json()
        assert del_resp_body.get("detail") == "User not found"

    def test_update_password(self, client, user1):
        # test user password update
        user1, password1 = user1
        current_password_hash = user1.password
        new_password = "newpass"
        client.login(username=user1.username, password=password1)
        resp: HttpResponse = client.put(
            f"/api/users/{user1.username}/password",
            {
                "current_password": password1,
                "new_password": new_password,
            },
            "application/json",
        )
        assert resp.status_code == 200
        user1.refresh_from_db()
        assert user1.password != current_password_hash

    def test_update_password_wrong_password(self, client, user1):
        # test user password update, wrong password
        user1, password1 = user1
        # current_password_hash = user1.password
        new_password = "newpass"
        client.login(username=user1.username, password=password1)
        resp: HttpResponse = client.put(
            f"/api/users/{user1.username}/password",
            {
                "current_password": "wrongpass",
                "new_password": new_password,
            },
            "application/json",
        )
        assert resp.status_code == 403
        resp_body = resp.json()
        assert resp_body.get("detail") == "Current password is incorrect"

    def test_update_password_different_user(self, client, user1, user2):

        # test_update_unauthorized_user
        user1, password1 = user1
        user2, password2 = user2
        # current_password_hash = user1.password
        new_password = "newpass"
        client.login(username=user2.username, password=password2)
        resp: HttpResponse = client.put(
            f"/api/users/{user1.username}/password",
            {
                "current_password": password1,
                "new_password": new_password,
            },
            "application/json",
        )
        assert resp.status_code == 403
        resp_body = resp.json()
        assert resp_body.get("detail") == "You do not have permission to update this user"

    def test_update_password_superuser(self, admin_client, user1):
        # test user password update
        user1, password1 = user1
        current_password_hash = user1.password
        new_password = "newpass"
        resp: HttpResponse = admin_client.put(
            f"/api/users/{user1.username}/password",
            {
                "current_password": password1,
                "new_password": new_password,
            },
            "application/json",
        )
        assert resp.status_code == 200
        user1.refresh_from_db()
        assert user1.password != current_password_hash

    def test_update_password_missing_current(self, client, user1):
        """User fails to provide current password"""
        user1, password1 = user1
        new_password = "newpass"
        client.login(username=user1.username, password=password1)
        resp: HttpResponse = client.put(
            f"/api/users/{user1.username}/password",
            {
                "new_password": new_password,
            },
            "application/json",
        )
        assert resp.status_code == 400
        resp_body = resp.json()
        assert resp_body.get("detail") == "Field required: current_password"

    def test_update_password_missing_new(self, client, user1):
        """User fails to provide new password"""
        user1, password1 = user1
        client.login(username=user1.username, password=password1)
        resp: HttpResponse = client.put(
            f"/api/users/{user1.username}/password",
            {
                "current_password": password1,
            },
            "application/json",
        )
        assert resp.status_code == 400
        resp_body = resp.json()
        assert resp_body.get("detail") == "Field required: new_password"

    def test_update_password_missing_both(self, client, user1):
        """User fails to provide both current and new password"""
        user1, password1 = user1
        client.login(username=user1.username, password=password1)
        resp: HttpResponse = client.put(
            f"/api/users/{user1.username}/password",
            {},
            "application/json",
        )
        assert resp.status_code == 400
        resp_body = resp.json()
        assert "Field required: current_password" in resp_body.get("detail")
        assert "Field required: new_password" in resp_body.get("detail")


class TestSession:

    @pytest.fixture()
    def user1(self, db):
        return create_test_user("user1", "password1")

    @pytest.fixture()
    def user2(self, db):
        return create_test_user("user2", "password2")

    def test_guest_session_creation(self, client):
        """# test guest user creation"""

        resp: HttpResponse = client.post("/api/guest_sessions")
        # assert no internal server error when running test
        assert resp.status_code == 201
        resp_body = resp.json()
        assert resp_body.get("options").get("is_guest")

        session_id = resp.cookies.get("sessionid")
        assert session_id is not None
        assert session_id.value != ""

    def test_creation(self, client, user1):
        """test session creation for non-guest user"""

        user, password = user1
        resp: HttpResponse = client.post(
            "/api/sessions", {"username": user.username, "password": password}, "application/json"
        )
        assert resp.status_code == 201
        session_id: Morsel = resp.cookies["sessionid"]
        assert session_id is not None
        assert session_id.value != ""
        resp_body = resp.json()
        assert resp_body.get("username") == user.username
        assert resp_body.get("options", {}).get("is_guest") in [None, False]  # Is None if no options set

    def test_creation_wrong_password(self, client, user1):
        user, _ = user1
        resp: HttpResponse = client.post(
            "/api/sessions", {"username": user.username, "password": "wrongpassword"}, "application/json"
        )
        assert resp.status_code == 401
        assert "sessionid" not in resp.cookies
        resp_body = resp.json()
        assert resp_body.get("detail") == "Unauthorized"
        assert set(resp_body.keys()).isdisjoint({"user", "options"})  # no overlapping values

    def test_creation_missing_password(self, client, user1):
        user, _ = user1
        resp: HttpResponse = client.post("/api/sessions", {"username": user.username}, "application/json")
        assert resp.status_code == 400
        assert "sessionid" not in resp.cookies
        resp_body = resp.json()
        assert "Field required: password" in resp_body.get("detail")

    def test_creation_empty_password(self, client, user1):
        user, _ = user1
        resp: HttpResponse = client.post(
            "/api/sessions", {"username": user.username, "password": ""}, "application/json"
        )
        assert resp.status_code == 401
        assert "sessionid" not in resp.cookies
        resp_body = resp.json()
        assert resp_body.get("detail") == "Unauthorized"
        assert set(resp_body.keys()).isdisjoint({"user", "options"})  # no overlapping values

    def test_creation_missing_username(self, client, user1):
        _, password = user1
        resp: HttpResponse = client.post("/api/sessions", {"password": password}, "application/json")
        assert resp.status_code == 400
        assert "sessionid" not in resp.cookies
        resp_body = resp.json()
        assert "Field required: username" in resp_body.get("detail")

    def test_creation_no_credentials(self, client):
        resp: HttpResponse = client.post("/api/sessions", "{}", "application/json")
        assert resp.status_code == 400
        resp_body = resp.json()
        assert "Field required: username" in resp_body.get("detail")
        assert "Field required: password" in resp_body.get("detail")

    def test_creation_during_active_session(self, client, user1, user2):
        user1, password1 = user1
        user2, password2 = user2
        resp1: HttpResponse = client.post(
            "/api/sessions", {"username": user1.username, "password": password1}, "application/json"
        )
        assert resp1.status_code == 201
        session_id1: Morsel = resp1.cookies["sessionid"]
        resp_username1 = resp1.json().get("username")

        resp2: HttpResponse = client.post(
            "/api/sessions", {"username": user2.username, "password": password2}, "application/json"
        )
        assert resp2.status_code == 201
        session_id2: Morsel = resp2.cookies["sessionid"]
        resp_username2 = resp2.json().get("username")

        assert resp_username1 == user1.username
        assert resp_username2 == user2.username
        assert resp_username1 != resp_username2
        assert session_id1.value != session_id2.value

    def test_deletion_active_session(self, client, user1):
        """test session deletion for non-guest user"""
        user, password = user1
        post_resp = client.post("/api/sessions", {"username": user.username, "password": password}, "application/json")
        post_session_id: Morsel = post_resp.cookies["sessionid"]

        del_resp: HttpResponse = client.delete("/api/sessions")

        assert del_resp.status_code == 200
        del_session_id: Morsel = del_resp.cookies["sessionid"]
        assert post_session_id != del_session_id
        assert del_session_id.value == ""
        del_resp_body = del_resp.json()
        assert not del_resp_body.get("username")  # empty string or missing or otherwise falsy
        assert not del_resp_body.get("options")  # empty dict of missing or otherwise falsy

    def test_deletion_no_active_session(self, client):
        """test attempted deletion without any active session and thus no auth"""

        resp: HttpResponse = client.delete("/api/sessions")

        assert resp.status_code == 401
        assert "sessionid" not in resp.cookies
        resp_body = resp.json()
        assert resp_body.get("detail") == "Unauthorized"
        assert set(resp_body.keys()).isdisjoint({"user", "options"})

    def test_get_active_session(self, client, user1):
        """test attempted active session retrieval with an active session"""

        user, password = user1
        post_resp = client.post("/api/sessions", {"username": user.username, "password": password}, "application/json")
        post_session_id: Morsel = post_resp.cookies["sessionid"]

        get_resp: HttpResponse = client.get("/api/sessions")
        assert get_resp.status_code == 200

        # NOTE: No SetCookie' header is sent in this response

        get_resp_body = get_resp.json()
        assert get_resp_body.get("username") == user.username
        assert get_resp_body.get("options", {}).get("is_guest") in [None, False]  # Is None if no options set

    def test_get_no_active_session(self, client):
        """test attempted active session retrieval with an active session"""

        get_resp: HttpResponse = client.get("/api/sessions")

        assert get_resp.status_code == 401
        assert len(get_resp.cookies) == 0
        get_resp_body = get_resp.json()
        assert get_resp_body.get("detail") == "Unauthorized"
        assert set(get_resp_body.keys()).isdisjoint({"user", "options"})
