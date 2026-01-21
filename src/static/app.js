document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message with fade out
      activitiesList.style.opacity = "0";
      setTimeout(() => {
        activitiesList.innerHTML = "";
        activitiesList.style.opacity = "1";

        // Populate activities list
        Object.entries(activities).forEach(([name, details], index) => {
          const activityCard = document.createElement("div");
          activityCard.className = "activity-card";
          activityCard.style.opacity = "0";
          activityCard.style.transform = "translateY(10px)";

          const spotsLeft = details.max_participants - details.participants.length;

          // Activity title
          const titleEl = document.createElement("h4");
          titleEl.textContent = name;
          activityCard.appendChild(titleEl);

          // Description
          const descriptionEl = document.createElement("p");
          descriptionEl.textContent = details.description;
          activityCard.appendChild(descriptionEl);

          // Schedule
          const scheduleEl = document.createElement("p");
          const scheduleStrong = document.createElement("strong");
          scheduleStrong.textContent = "Schedule:";
          scheduleEl.appendChild(scheduleStrong);
          scheduleEl.appendChild(document.createTextNode(" " + details.schedule));
          activityCard.appendChild(scheduleEl);

          // Availability
          const availabilityEl = document.createElement("p");
          const availabilityStrong = document.createElement("strong");
          availabilityStrong.textContent = "Availability:";
          availabilityEl.appendChild(availabilityStrong);
          availabilityEl.appendChild(document.createTextNode(" " + spotsLeft + " spots remaining"));
          activityCard.appendChild(availabilityEl);

          // Participants section
          const participantsContainer = document.createElement("div");
          participantsContainer.className = "activity-participants";

          const participantsHeader = document.createElement("h5");
          participantsHeader.textContent = "Enrolled Students";
          participantsContainer.appendChild(participantsHeader);

          if (details.participants.length > 0) {
            const ul = document.createElement("ul");
            details.participants.forEach((email) => {
              const li = document.createElement("li");

              const emailSpan = document.createElement("span");
              emailSpan.textContent = email;
              li.appendChild(emailSpan);

              const deleteButton = document.createElement("button");
              deleteButton.className = "delete-icon";
              deleteButton.dataset.activity = name;
              deleteButton.dataset.email = email;
              deleteButton.title = "Remove participant";
              deleteButton.setAttribute("aria-label", "Remove " + email);
              deleteButton.textContent = "✕";

              li.appendChild(deleteButton);
              ul.appendChild(li);
            });
            participantsContainer.appendChild(ul);
          } else {
            const noParticipants = document.createElement("p");
            noParticipants.className = "no-participants";
            noParticipants.textContent = "No participants yet. Be the first to enroll.";
            participantsContainer.appendChild(noParticipants);
          }

          activityCard.appendChild(participantsContainer);

          activitiesList.appendChild(activityCard);

          // Staggered animation
          setTimeout(() => {
            activityCard.style.transition = "all 0.4s cubic-bezier(0.4, 0, 0.2, 1)";
            activityCard.style.opacity = "1";
            activityCard.style.transform = "translateY(0)";
          }, index * 80);

          // Add option to select dropdown
          const option = document.createElement("option");
          option.value = name;
          option.textContent = name;
          activitySelect.appendChild(option);
        });
      }, 300);
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        // Refresh the activities list
        await fetchActivities();
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle delete participant
  activitiesList.addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-icon")) {
      const activity = event.target.dataset.activity;
      const email = event.target.dataset.email;

      if (!confirm(`Are you sure you want to unregister ${email} from ${activity}?`)) {
        return;
      }

      try {
        const response = await fetch(
          `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
          {
            method: "DELETE",
          }
        );

        const result = await response.json();

        if (response.ok) {
          // Refresh the activities list
          await fetchActivities();
          messageDiv.textContent = result.message;
          messageDiv.className = "success";
        } else {
          messageDiv.textContent = result.detail || "An error occurred";
          messageDiv.className = "error";
        }

        messageDiv.classList.remove("hidden");

        // Hide message after 5 seconds
        setTimeout(() => {
          messageDiv.classList.add("hidden");
        }, 5000);
      } catch (error) {
        messageDiv.textContent = "Failed to unregister. Please try again.";
        messageDiv.className = "error";
        messageDiv.classList.remove("hidden");
        console.error("Error unregistering:", error);
      }
    }
  });

  // Initialize app
  fetchActivities();
});
