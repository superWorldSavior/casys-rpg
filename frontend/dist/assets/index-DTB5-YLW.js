import{r as x,j as a,a as m}from"./index-CTdJZ5md.js";import{r as s}from"./vendor-BBF-xwg4.js";import{i as y,j,d as b,b as g,e as C,w as P,p as S,C as w}from"./mui-CG_8jc0N.js";import"./mui-deps-DIjIPAY3.js";import"./router-DvyW0KNU.js";var l={},D=y;Object.defineProperty(l,"__esModule",{value:!0});var h=l.default=void 0,E=D(x()),U=j;h=l.default=(0,E.default)((0,U.jsx)("path",{d:"M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96M14 13v4h-4v-4H7l5-5 5 5z"}),"CloudUpload");const B=()=>{const[n,i]=s.useState(!1),[u,r]=s.useState(null),[d,p]=s.useState("");return a(w,{children:m(g,{sx:{mb:4},children:[a(b,{variant:"h4",gutterBottom:!0,sx:{fontWeight:500,color:"primary.main",mb:3},children:"Profil"}),a(g,{sx:{mt:4},children:m(C,{variant:"contained",color:"primary",component:"label",startIcon:a(h,{}),disabled:n,children:[n?"Uploading...":"Ajouter un livre",a("input",{type:"file",hidden:!0,accept:".pdf",onChange:async c=>{const t=c.target.files[0];if(!t)return;if(t.type!=="application/pdf"){r("Please select a valid PDF file");return}const f=new FormData;f.append("pdf_files",t);try{i(!0),r(null);const e=await fetch("/api/books/upload",{method:"POST",body:f});if(!e.ok){const o=await e.json();throw new Error((o==null?void 0:o.message)||`Upload failed: ${e.status}`)}const v=await e.json();p(v.message||"PDF uploaded successfully"),c.target.value=""}catch(e){console.error("Error uploading PDF:",e),r(e.message||"Error uploading file")}finally{i(!1)}}})]})}),a(P,{open:!!d,autoHideDuration:6e3,onClose:()=>p(""),message:d}),u&&a(S,{severity:"error",sx:{mt:3},onClose:()=>r(null),children:u})]})})};export{B as default};
//# sourceMappingURL=index-DTB5-YLW.js.map
