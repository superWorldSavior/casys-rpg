import{n as e,j as s,o as i,p as a,C as t,P as r,d as o,h as n,b as l,q as d,I as m,s as p,t as u,f as c}from"./mui-baHMyI2e.js";import{r as x}from"./vendor-Dq37Ohfu.js";import{u as h}from"./index-DN1I9J6c.js";import{u as b}from"./router-B6Hy40oI.js";import"./mui-deps-BEMH35sO.js";const f=e(s.jsx("path",{d:"M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5M12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5m0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3"}),"Visibility"),j=e(s.jsx("path",{d:"M12 7c2.76 0 5 2.24 5 5 0 .65-.13 1.26-.36 1.83l2.92 2.92c1.51-1.26 2.7-2.89 3.43-4.75-1.73-4.39-6-7.5-11-7.5-1.4 0-2.74.25-3.98.7l2.16 2.16C10.74 7.13 11.35 7 12 7M2 4.27l2.28 2.28.46.46C3.08 8.3 1.78 10.02 1 12c1.73 4.39 6 7.5 11 7.5 1.55 0 3.03-.3 4.38-.84l.42.42L19.73 22 21 20.73 3.27 3zM7.53 9.8l1.55 1.55c-.05.21-.08.43-.08.65 0 1.66 1.34 3 3 3 .22 0 .44-.03.65-.08l1.55 1.55c-.67.33-1.41.53-2.2.53-2.76 0-5-2.24-5-5 0-.79.2-1.53.53-2.2m4.31-.78 3.15 3.15.02-.16c0-1.66-1.34-3-3-3z"}),"VisibilityOff"),g=()=>{const e=i(),g=a(e.breakpoints.down("sm")),y=b(),{login:v}=h(),[w,C]=x.useState({email:"",password:""}),[M,I]=x.useState(!1),[R,S]=x.useState(!1),[W,z]=x.useState(""),q=e=>{const{name:s,value:i}=e.target;C((e=>({...e,[s]:i}))),z("")};return s.jsx(t,{component:"main",maxWidth:"xs",sx:{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",p:g?2:3},children:s.jsxs(r,{elevation:3,sx:{p:g?3:4,display:"flex",flexDirection:"column",alignItems:"center",width:"100%",borderRadius:g?2:3,position:"relative"},children:[s.jsx(o,{component:"h1",variant:g?"h5":"h4",sx:{mb:3,fontWeight:600,color:e.palette.primary.main},children:"Connexion"}),W&&s.jsx(n,{severity:"error",sx:{width:"100%",mb:2},children:W}),s.jsxs(l,{component:"form",onSubmit:async e=>{e.preventDefault(),S(!0),z("");try{await new Promise((e=>setTimeout(e,1e3)));const e={id:"1",email:w.email,username:"User"};await v(e),y("/home")}catch(s){z("Identifiants invalides. Veuillez réessayer.")}finally{S(!1)}},sx:{width:"100%",mt:1},children:[s.jsx(d,{margin:"normal",required:!0,fullWidth:!0,id:"email",label:"Email",name:"email",autoComplete:"email",autoFocus:!0,value:w.email,onChange:q,disabled:R,sx:{mb:2,"& .MuiOutlinedInput-root":{borderRadius:e.shape.borderRadius}}}),s.jsx(d,{margin:"normal",required:!0,fullWidth:!0,name:"password",label:"Mot de passe",type:M?"text":"password",id:"password",autoComplete:"current-password",value:w.password,onChange:q,disabled:R,InputProps:{endAdornment:s.jsx(m,{position:"end",children:s.jsx(p,{"aria-label":"toggle password visibility",onClick:()=>{I(!M)},edge:"end",children:M?s.jsx(j,{}):s.jsx(f,{})})})},sx:{mb:3,"& .MuiOutlinedInput-root":{borderRadius:e.shape.borderRadius}}}),s.jsx(u,{type:"submit",fullWidth:!0,variant:"contained",disabled:R,sx:{mb:2,py:1.5,position:"relative",borderRadius:e.shape.borderRadius},children:R?s.jsx(c,{size:24,sx:{position:"absolute",top:"50%",left:"50%",marginTop:"-12px",marginLeft:"-12px"}}):"Se connecter"})]})]})})};export{g as default};
