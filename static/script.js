//Pour le Multiple Select
$(document).ready(function() {
    $('.etiquette').select2({
      tags: true
    });
});

$(document).ready(function() {
    $('.filtreEtiquette').select2({
    });
});



(function (d) {
  "use strict";
  d.querySelector("#addDiv").addEventListener("click", addDiv);
  function addDiv() {
    var p = d.createElement("div");
    var x = d.createElement("INPUT");
    var z = d.createElement("TEXTAREA");
    var btn = document.createElement("BUTTON");
    var t = document.createTextNode("SUPP");
    var y =parseInt(document.getElementById("nb_quest").value)+1;
    x.setAttribute("type", "checkbox");
    z.setAttribute("type", "text");
    btn.appendChild(t);
    btn.name = "btn"+ y;
    btn.id = "btn"+ y;
    btn.setAttribute("class", "bouttonSUPP")
    p.setAttribute("class", "elementReponse");
    btn.type = "button";
    btn.setAttribute("onclick","supp(this.id);");
    x.name = "checkbox" + y;
    x.id = "checkbox" + y;
    p.id = "elementReponse" + y;
    z.name = "rep" + y;
    z.id = "rep" + y;
    z.required = "false";
    document.getElementById("nb_quest").value=y ;
    p.append(x);
    p.append(z);
    p.append(btn);
    d.getElementById("reponses").appendChild(p);


  }
  
})(document); 


function nvQ() {
    var liS = document.querySelectorAll('select[class="nvChoix"]')
    if (liS[liS.length-1].value != "" ){
    var y =parseInt(document.getElementById("nb_quest_sequence").value)+1;
    var nvS = document.getElementById("sequence" + (document.getElementById("nb_quest_sequence").value)).cloneNode(true);
    nvS.name = "sequence" + y;
    nvS.id="sequence" + y;
    var nvSupp = document.getElementById("btnSel1").cloneNode(true);
    nvSupp.id="btnSel" + y;
    nvSupp.setAttribute("value", y);
    document.getElementById("nb_quest_sequence").value = y;
    document.getElementById("selectSequence").appendChild(nvS);
    document.getElementById("selectSequence").appendChild(nvSupp);
    }

  
}


function suppSel(clicked_id) {
    num = document.getElementById(clicked_id).value;
    console.log('num = ' +num);
    var sel = "sequence"+num;
    console.log('sel = '+ sel);
    var fin = document.getElementById("nb_quest_sequence").value;
    j = parseInt(num)+1;
    console.log('j = '+j);
    for (j; j<fin; j++) {
      var verif = document.getElementById("sequence"+(j).toString());
      console.log('verif = '+ verif);
      if(!verif){
        console.log('verif is false ');
        document.getElementById(sel).outerHTML = "";
        document.getElementById(clicked_id).outerHTML = "";
        fin=fin-1;
        document.getElementById("nb_quest_sequence").value= fin;
      }

      if(verif){
        console.log('verif is true ');
        document.getElementById(sel).outerHTML = "";
        document.getElementById(clicked_id).outerHTML = "";
        document.getElementById("sequence"+j).setAttribute("name","sequence"+(j-1).toString());
        console.log("sequence"+j+" = "+ "sequence"+(j-1).toString());
        document.getElementById("sequence"+j).setAttribute("value", j-1);
        document.getElementById("sequence"+j).id = "sequence"+(j-1).toString();
        document.getElementById("btnSel"+j).setAttribute("value", j-1);
        document.getElementById("btnSel"+j).id = "btnSel"+(j-1).toString();
        fin=fin-1;
        document.getElementById("nb_quest_sequence").value= fin;
        
      }
    }

}




function supp(clicked_id) {
    num = clicked_id;
    console.log('num = ' +num);
    var chars = num.split('');
    var char = "elementReponse"+chars[3];
    console.log('char = '+ char);
    var fin = document.getElementById("nb_quest").value;
    j = parseInt(chars[3])+1;
    console.log('j = '+j);
    for (j; j<fin+2; j++) {
      var verif = document.getElementById("elementReponse"+(j-1).toString());
      console.log('verif = '+ verif);
      if(!verif){
        console.log('verif is false ');
      }

      if(verif){
        console.log('verif is true ');
        document.getElementById(char).outerHTML = "";
        fin=fin-1;
        document.getElementById("nb_quest").value= fin;
        document.getElementById("elementReponse"+j).setAttribute("name","elementReponse"+(j-1).toString());
        document.getElementById("elementReponse"+j).id = "elementReponse"+(j-1).toString();
        console.log("elementReponse"+j+" = "+ "elementReponse"+(j-1).toString());
        document.getElementById("checkbox"+j).setAttribute("name","checkbox"+(j-1).toString());
        document.getElementById("checkbox"+j).id = "checkbox"+(j-1).toString();
        document.getElementById("rep"+j).setAttribute("name","rep"+(j-1).toString());
        document.getElementById("rep"+j).id = "rep"+(j-1).toString();
        document.getElementById("btn"+j).setAttribute("name","btn"+(j-1).toString());
        document.getElementById("btn"+j).id = "btn"+(j-1).toString();
      }
    }

}

function filtre() {
const selected = document.querySelectorAll('#filtreEtiquette option:checked');
const values = Array.from(selected).map(el => el.value);
const selectOpt = document.getElementsByClassName(values.join(' '));
const allOpt = document.getElementsByClassName("all");

console.log(values);


console.log(values);

for (var i = 0; i < allOpt.length; ++i) {
  document.getElementsByClassName("all")[i].style.display = 'none';
}

if (values.length === 0){
  values.push("all");
  for (var i = 0; i < allOpt.length; ++i) {
  document.getElementsByClassName("all")[i].style.display = 'block';
}
}

for (var i = 0; i < selectOpt.length; ++i) {
  document.getElementsByClassName(values.join(' '))[i].style.display = 'block';
}

}

function qcm() {
  document.getElementById("type_q").style.display = "none";
  document.getElementById("qcm").style.display = "block";
  document.getElementById("ajtQuestion").style.display = "block";
}

function num() {
  document.getElementById("type_q").style.display = "none";
  document.getElementById("numerique").style.display = "block";
  document.getElementById("ajtQuestion").style.display = "block";
}




