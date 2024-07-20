document.addEventListener("DOMContentLoaded", function() {
    const nationalNumberInput = document.querySelector("#id_national_number");
    const dobInput = document.querySelector("#id_date_of_birth");

    function formatNationalNumber(e) {
        var input = e.target.value.replace(/\D/g, '');
        var formattedInput = input;

        if (input.length > 2) {
            formattedInput = input.substring(0, 2) + '.' + input.substring(2);
        }
        if (input.length > 4) {
            formattedInput = formattedInput.substring(0, 5) + '.' + input.substring(4);
        }
        if (input.length > 6) {
            formattedInput = formattedInput.substring(0, 8) + '-' + input.substring(6);
        }
        if (input.length > 9) {
            formattedInput = formattedInput.substring(0, 12) + '.' + input.substring(9);
        }

        e.target.value = formattedInput.substring(0, 15);

        if (input.length >= 6) {
            var month = parseInt(input.substring(2, 4), 10);
            var day = parseInt(input.substring(4, 6), 10);

            if (month < 1 || month > 12) {
                e.target.setCustomValidity("The month must be between 01 and 12.");
            } else if (day < 1 || day > 31) {
                e.target.setCustomValidity("The day must be between 01 and 31.");
            } else {
                e.target.setCustomValidity("");
            }
        }
    }


    function validateDOB(e) {
        var input = e.target.value;

        if (!input) {
            return;
        }

        var dateParts = input.split("-");
        var year = parseInt(dateParts[0], 10);
        var month = parseInt(dateParts[1], 10) - 1;
        var day = parseInt(dateParts[2], 10);

        var inputDate = new Date(year, month, day);
        var currentDate = new Date();

        var minAge = 17;
        var maxAge = 90;

        var minDate = new Date(currentDate.getFullYear() - maxAge, currentDate.getMonth(), currentDate.getDate());
        var maxDate = new Date(currentDate.getFullYear() - minAge, currentDate.getMonth(), currentDate.getDate());

        if (inputDate < minDate || inputDate > maxDate) {
            alert("Vous n'avez pas l'âge requis à l'inscription - Date of birth incorrect.");
            e.target.value = "";
        }
    }

    if (nationalNumberInput) {
        nationalNumberInput.addEventListener("input", formatNationalNumber);
    }

    if (dobInput) {
        dobInput.addEventListener("blur", validateDOB);
    }
});