<%@ Page Title="" Language="C#" MasterPageFile="~/MasterPage.master" AutoEventWireup="true" CodeFile="guanliyuan.aspx.cs" Inherits="guanliyuan" %>

<asp:Content ID="Content1" ContentPlaceHolderID="head" Runat="Server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" Runat="Server">
    <div align="center" 
    style="padding: 30px; margin: 20px; top: 20px; background-image: url('背景图/ac423248d47b30dbe12db1b9c1ccd282.jpg');">
    <asp:Label ID="Label1" runat="server" Text="账号："></asp:Label>
    <asp:TextBox ID="TextBox1" runat="server"></asp:TextBox>
    <br />
    <asp:Label ID="Label3" runat="server" Text="密码："></asp:Label>
    <asp:TextBox ID="TextBox3" runat="server"></asp:TextBox>
    <br />
    <asp:Button ID="Button1" runat="server" Text="确定" onclick="Button1_Click" />
    <br />
    </div>
</asp:Content>

