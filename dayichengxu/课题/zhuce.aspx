<%@ Page Title="" Language="C#" MasterPageFile="~/MasterPage.master" AutoEventWireup="true" CodeFile="zhuce.aspx.cs" Inherits="zhuce" %>

<asp:Content ID="Content1" ContentPlaceHolderID="head" Runat="Server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" Runat="Server">
<div align="center" 
        
        style="height: 578px; background-image: url('图片/0008020232552101_b.jpg'); font-size: 50px; color: #FF0000;">
    <br />
    注册<br />
    <table style="width: 557px; height: 135px;">
    <tr><td style="font-size: 20px">账号：<asp:TextBox ID="TextBox1" runat="server"></asp:TextBox>
        </td>
     </tr>
      <tr><td style="font-size: 20px">密码：<asp:TextBox ID="TextBox2" runat="server"></asp:TextBox>
          </td>
     </tr>
      <tr><td style="font-size: 20px">确认密码：<asp:TextBox ID="TextBox3" runat="server"></asp:TextBox>
          <asp:CompareValidator ID="CompareValidator1" runat="server" 
              ControlToCompare="TextBox2" ControlToValidate="TextBox3" ErrorMessage="密码不一致"></asp:CompareValidator>
          <br />
          <asp:Button ID="Button1" runat="server" Height="21px" Text="注册" 
              onclick="Button1_Click" />
          </td>
     </tr>
    </table>
    <br />
    </div>
</asp:Content>

