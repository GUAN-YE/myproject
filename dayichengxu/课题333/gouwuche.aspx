<%@ Page Title="" Language="C#" MasterPageFile="~/MasterPage.master" AutoEventWireup="true" CodeFile="gouwuche.aspx.cs" Inherits="gouwuche" %>

<asp:Content ID="Content1" ContentPlaceHolderID="head" Runat="Server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" Runat="Server">
    <div align="center" 
    style="background-image: url('背景图/ed4d67cd64cf1468b890724218dee87c.jpg'); height: 265px;">
    <asp:GridView ID="GridView1" runat="server" AutoGenerateColumns="False" 
        onrowcancelingedit="GridView1_RowCancelingEdit" 
        onrowdeleting="GridView1_RowDeleting" onrowediting="GridView1_RowEditing" 
        onrowupdating="GridView1_RowUpdating">
        <Columns>
            <asp:BoundField DataField="xinghao" HeaderText="型号" />
            <asp:BoundField DataField="jiage" HeaderText="价格" />
            <asp:BoundField DataField="shuliang" HeaderText="数量" />
            <asp:BoundField DataField="xioaji" HeaderText="小计" />
            <asp:CommandField HeaderText="编辑" ShowEditButton="True" />
            <asp:CommandField HeaderText="删除" ShowDeleteButton="True" />
        </Columns>
    </asp:GridView>
    <asp:GridView ID="GridView2" runat="server">
    </asp:GridView>
   
    <asp:Button ID="Button1" runat="server" onclick="Button1_Click1" Text="购买" />
    </div>
</asp:Content>

