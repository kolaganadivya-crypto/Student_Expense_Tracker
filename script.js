document.getElementById("registrationForm").addEventListener("submit", function(event){

    event.preventDefault();

    let fname = document.getElementById("fname").value;
    let lname = document.getElementById("lname").value;
    let regno = document.getElementById("regno").value;
    let email = document.getElementById("email").value;
    let mobile = document.getElementById("mobile").value;
    let course = document.getElementById("course").value;
    let address = document.getElementById("address").value;

    document.getElementById("output").innerHTML =
    `
    <h2 style="color:blue;">Student Details</h2>

    <p style="color:red;">First Name : ${fname}</p>

    <p style="color:green;">Last Name : ${lname}</p>

    <p style="color:purple;">Registration Number : ${regno}</p>

    <p style="color:orange;">Email ID : ${email}</p>

    <p style="color:black;">Mobile Number : ${mobile}</p>

    <p style="color:darkblue;">Interested Course : ${course}</p>

    <p style="color:darkgreen;">Permanent Address : ${address}</p>
    `;
});