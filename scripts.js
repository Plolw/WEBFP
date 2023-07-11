function check(){
    if (document.getElementById('password').value == document.getElementById('confirm_password').value) {
      document.getElementById('message').style.color = 'green';
      document.getElementById('message').innerHTML = 'matching';
      document.getElementById('validation').disabled = false;
      
    } else {
      document.getElementById('message').style.color = 'red';
      document.getElementById('message').innerHTML = 'not matching';
      document.getElementById('validation').disabled = true;
    }
  }

setInterval(check, 10);