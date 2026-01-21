"""Tests for the High School Management System API endpoints"""


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Soccer Team" in data
        assert "Drama Club" in data

    def test_activity_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_for_valid_activity(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Soccer Team"

    def test_signup_for_invalid_activity(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistentActivity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_duplicate_signup(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Soccer Team/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Student already signed up for this activity"

    def test_signup_persists_in_activities_list(self, client):
        """Test that signup actually adds the student to the activity"""
        email = "persistent@mergington.edu"
        
        client.post(
            "/activities/Drama Club/signup",
            params={"email": email}
        )
        
        # Verify the student is in the activities list
        response = client.get("/activities")
        data = response.json()
        assert email in data["Drama Club"]["participants"]

    def test_signup_with_spaces_in_activity_name(self, client):
        """Test signup works with activity names containing spaces"""
        response = client.post(
            "/activities/Drama Club/signup",
            params={"email": "drama@mergington.edu"}
        )
        assert response.status_code == 200

    def test_signup_when_activity_is_full(self, client):
        """Test that signup fails when activity has reached max capacity"""
        # Drama Club has max_participants = 15
        # First, fill up the activity to its maximum capacity
        response = client.get("/activities")
        drama_club = response.json()["Drama Club"]
        current_count = len(drama_club["participants"])
        max_capacity = drama_club["max_participants"]
        
        # Fill remaining spots
        for i in range(max_capacity - current_count):
            email = f"student{i}@mergington.edu"
            response = client.post(
                "/activities/Drama Club/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Now try to add one more student - should fail
        response = client.post(
            "/activities/Drama Club/signup",
            params={"email": "overflow@mergington.edu"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Activity is full"


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_from_activity(self, client):
        """Test successful unregistration from an activity"""
        email = "unregister@mergington.edu"
        
        # First signup
        client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Art Studio/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from Art Studio"

    def test_unregister_from_invalid_activity(self, client):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/NonExistentActivity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_when_not_signed_up(self, client):
        """Test unregister when student is not signed up returns 400"""
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": "notsignedup@mergington.edu"}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"

    def test_unregister_removes_from_participants_list(self, client):
        """Test that unregister actually removes the student from the activity"""
        email = "remove@mergington.edu"
        
        # Signup
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        # Unregister
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        # Verify the student is not in the activities list
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_existing_participant(self, client):
        """Test unregistering a pre-existing participant"""
        # alex@mergington.edu is already in Soccer Team
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200


class TestIntegrationScenarios:
    """Integration tests for complex user scenarios"""

    def test_complete_user_journey(self, client):
        """Test a complete user journey: view, signup, unregister"""
        email = "journey@mergington.edu"
        
        # View activities
        response = client.get("/activities")
        assert response.status_code == 200
        
        # Signup for an activity
        signup_response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()["Programming Class"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            "/activities/Programming Class/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()["Programming Class"]["participants"]

    def test_signup_multiple_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multi@mergington.edu"
        activities = ["Soccer Team", "Drama Club", "Chess Club"]
        
        for activity in activities:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        response = client.get("/activities")
        data = response.json()
        for activity in activities:
            assert email in data[activity]["participants"]
